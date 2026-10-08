"""
Checkout and order workflows for the Sell app.

Wraps the raw StripeClient with everything project-specific: building
checkout sessions from the project's catalog, recording pending orders,
applying payment outcomes from webhooks (or a manual sync when webhooks
can't reach us), and upserting customers from completed checkouts.
"""

import datetime
import hashlib
import logging
from decimal import Decimal
from urllib.parse import urlsplit

from django.conf import settings as django_settings
from django.db import IntegrityError, transaction
from django.utils import timezone

from imagi.redirect_urls import UnsafeRedirectError, resolve_redirect_url

from ..models import Customer, Order, OrderItem, Product, Subscription, UsageEvent
from .stripe_client import StripeClient, StripeClientError

logger = logging.getLogger(__name__)

# Guardrails for a single checkout session.
MAX_LINE_ITEMS = 20
MAX_QUANTITY = 100

# Stripe won't charge less than ~$0.50 (or equivalent) per session.
MIN_PRICE_CENTS = 50

# One usage report can't claim more than this many units.
MAX_USAGE_QUANTITY = 1_000_000


class SellServiceError(Exception):
    """A user-facing problem (bad config, bad cart, Stripe rejection)."""


def webhook_base_url() -> str:
    base = getattr(django_settings, 'SELL_WEBHOOK_BASE_URL', '')
    return base.rstrip('/') if base else ''


def stripe_webhook_url(project_id: int) -> str:
    """Public URL to register as the Stripe webhook endpoint; empty when unset."""
    base = webhook_base_url()
    if not base:
        return ''
    return f'{base}/api/v1/sell/webhooks/{project_id}/stripe/'


def connect_webhook_url() -> str:
    """
    The one endpoint Stripe sends every connected account's events to;
    registered once on Imagi's platform account. Empty when unset.
    """
    base = webhook_base_url()
    if not base:
        return ''
    return f'{base}/api/v1/sell/webhooks/connect/'


def default_success_url(project_id: int) -> str:
    frontend = django_settings.FRONTEND_URL.rstrip('/')
    # Stripe substitutes the session id into the placeholder on redirect.
    return f'{frontend}/checkout/{project_id}/success?session_id={{CHECKOUT_SESSION_ID}}'


def default_cancel_url(project_id: int) -> str:
    frontend = django_settings.FRONTEND_URL.rstrip('/')
    return f'{frontend}/checkout/{project_id}/cancel'


def platform_secret_key() -> str:
    return getattr(django_settings, 'STRIPE_SECRET_KEY', '') or ''


def _ts(value):
    """A Stripe unix timestamp as an aware datetime (None stays None)."""
    if not value:
        return None
    try:
        return datetime.datetime.fromtimestamp(int(value), tz=datetime.timezone.utc)
    except (TypeError, ValueError, OverflowError):
        return None


def _id(value) -> str:
    """A Stripe reference that may be an id string or an expanded object."""
    if isinstance(value, str):
        return value
    return (value or {}).get('id', '') if isinstance(value, dict) else ''


class SellService:
    """Selling operations for a single project."""

    def __init__(self, project):
        self.project = project
        self.config = getattr(project, 'sell_settings', None)

    # -- setup ---------------------------------------------------------------

    def _client(self) -> StripeClient:
        config = self.config
        if config and config.uses_connect:
            if not platform_secret_key():
                raise SellServiceError(
                    'Imagi\'s Stripe platform key is not set up on this server.'
                )
            if not config.connect_charges_enabled:
                raise SellServiceError(
                    'Your Stripe account is connected but can\'t take payments yet. '
                    'Finish setting it up from the Sell console.'
                )
            return StripeClient(platform_secret_key(), config.connect_account_id)
        if not config or not config.is_configured:
            raise SellServiceError(
                'Stripe is not connected. Connect your Stripe account from '
                'the Sell console first.'
            )
        return StripeClient(config.stripe_secret_key)

    def _account_ref(self) -> str:
        """Which Stripe account this project's objects live on."""
        if self.config and self.config.uses_connect:
            return self.config.connect_account_id
        key = self.config.stripe_secret_key if self.config else ''
        return 'key:' + hashlib.sha256(key.encode()).hexdigest()[:16] if key else ''

    def redirect_origins(self, *urls) -> list:
        """
        Origins, besides Imagi's own, that Stripe may send customers back to:
        the business's published app, and, while payments are in test mode,
        a loopback address (the app's local preview). A loopback redirect
        can't hand a real customer to someone else's site.
        """
        origins = []
        if self.config and self.config.app_url:
            parts = urlsplit(self.config.app_url)
            if parts.scheme in ('http', 'https') and parts.netloc:
                origins.append(f'{parts.scheme}://{parts.netloc}')
        if self.config and self.config.is_test_mode:
            for url in urls:
                parts = urlsplit(str(url or '').strip())
                if parts.scheme in ('http', 'https') and parts.hostname in (
                    'localhost', '127.0.0.1', '::1'
                ):
                    origins.append(f'{parts.scheme}://{parts.netloc}')
        return origins

    def verify(self) -> dict:
        """
        Check the stored secret key against Stripe and cache the account
        identity for display.
        """
        if self.config and self.config.uses_connect:
            from .connect_service import ConnectService
            account = ConnectService(self.project).refresh()
            return {
                'account_name': self.config.account_name,
                'account_email': self.config.account_email,
                'charges_enabled': bool(account.get('charges_enabled')),
            }
        client = self._client()
        try:
            account = client.fetch_account()
        except StripeClientError as exc:
            raise SellServiceError(f'Stripe rejected the credentials: {exc}') from exc

        dashboard = (account.get('settings') or {}).get('dashboard') or {}
        business = account.get('business_profile') or {}
        self.config.account_name = (
            dashboard.get('display_name') or business.get('name') or ''
        )
        self.config.account_email = account.get('email') or ''
        self.config.last_verified_at = timezone.now()
        self.config.save(update_fields=[
            'account_name', 'account_email', 'last_verified_at', 'updated_at',
        ])

        return {
            'account_name': self.config.account_name,
            'account_email': self.config.account_email,
            'charges_enabled': bool(account.get('charges_enabled')),
        }

    # -- checkout --------------------------------------------------------------

    def create_checkout(self, items: list, success_url: str = '',
                        cancel_url: str = '', customer_email: str = '') -> Order:
        """
        Create a pending Order and its Stripe Checkout session from
        [{'product_id': int, 'quantity': int}, ...]. Returns the order with
        `checkout_url` set as a transient attribute.

        Prices always come from the project's catalog — never from the
        caller — so a tampered request can't change what gets charged.

        The redirect URLs are confined to this app's own origin here as well as
        at the view, so a future caller cannot reintroduce the open redirect by
        reaching the service directly.
        """
        client = self._client()
        customer_email = (customer_email or '').strip().lower()

        extra_origins = self.redirect_origins(success_url, cancel_url)
        try:
            success_url = resolve_redirect_url(
                success_url, default_success_url(self.project.id), extra_origins
            )
            cancel_url = resolve_redirect_url(
                cancel_url, default_cancel_url(self.project.id), extra_origins
            )
        except UnsafeRedirectError as exc:
            raise SellServiceError(str(exc)) from exc

        if not isinstance(items, list) or not items:
            raise SellServiceError('Provide a non-empty "items" list.')
        if len(items) > MAX_LINE_ITEMS:
            raise SellServiceError(f'A checkout is limited to {MAX_LINE_ITEMS} line items.')

        currency = self.config.currency or 'usd'
        line_items = []
        resolved = []
        for row in items:
            if not isinstance(row, dict):
                raise SellServiceError('Each item must be an object with product_id and quantity.')
            try:
                product_id = int(row.get('product_id'))
            except (TypeError, ValueError):
                raise SellServiceError('Each item needs a numeric product_id.')
            try:
                quantity = int(row.get('quantity', 1))
            except (TypeError, ValueError):
                raise SellServiceError('Item quantity must be a number.')
            if not 1 <= quantity <= MAX_QUANTITY:
                raise SellServiceError(f'Item quantity must be between 1 and {MAX_QUANTITY}.')

            product = self.project.sell_products.filter(
                id=product_id, is_active=True,
            ).first()
            if not product:
                raise SellServiceError('One of the products is unavailable.')

            if product.is_usage:
                # Metered: Stripe bills what's reported, so there's no
                # quantity, and the price must be a real Price on a meter.
                resolved.append((product, 1))
                line_items.append({'price': self.ensure_usage_price(client, product)})
                continue

            resolved.append((product, quantity))
            product_data = {'name': product.name}
            if product.description:
                product_data['description'] = product.description[:500]
            if product.image_url:
                product_data['images'] = [product.image_url]
            price_data = {
                'currency': currency,
                'unit_amount': product.price_cents,
                'product_data': product_data,
            }
            if product.is_recurring:
                price_data['recurring'] = {'interval': product.billing_interval}
            line_items.append({
                'quantity': quantity,
                'price_data': price_data,
            })

        # Any recurring item switches the whole session to subscription mode
        # (Stripe allows one-time items alongside a subscription, but not the
        # reverse: recurring prices are invalid in payment mode).
        mode = (
            'subscription' if any(product.is_recurring for product, _ in resolved)
            else 'payment'
        )
        if mode == 'subscription' and len([p for p, _ in resolved if p.is_recurring]) > 1:
            raise SellServiceError('A checkout can include one subscription plan at a time.')
        # Usage is billed later, so it adds nothing to what's paid today.
        amount_total = sum(
            product.price_cents * quantity for product, quantity in resolved
            if not product.is_usage
        )

        with transaction.atomic():
            order = Order.objects.create(
                project=self.project,
                status=Order.STATUS_PENDING,
                amount_total_cents=amount_total,
                currency=currency,
                customer_email=customer_email,
            )
            OrderItem.objects.bulk_create([
                OrderItem(
                    order=order,
                    product=product,
                    product_name=product.name,
                    unit_price_cents=product.price_cents,
                    quantity=quantity,
                )
                for product, quantity in resolved
            ])

        metadata = {
            'imagi_project_id': str(self.project.id),
            'imagi_order_id': str(order.id),
        }
        subscription_metadata = None
        if mode == 'subscription':
            plan = next(product for product, _ in resolved if product.is_recurring)
            subscription_metadata = {
                'imagi_project_id': str(self.project.id),
                'imagi_product_id': str(plan.id),
            }
        try:
            session = client.create_checkout_session(
                line_items=line_items,
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata,
                customer_email=customer_email,
                mode=mode,
                subscription_metadata=subscription_metadata,
            )
        except StripeClientError as exc:
            # The session never existed, so neither did the checkout attempt.
            order.delete()
            raise SellServiceError(f'Stripe could not start the checkout: {exc}') from exc

        order.stripe_checkout_session_id = session.get('id', '')
        order.save(update_fields=['stripe_checkout_session_id', 'updated_at'])
        order.checkout_url = session.get('url', '')
        return order

    # -- payment outcomes --------------------------------------------------------

    def apply_session(self, order: Order, session) -> bool:
        """
        Apply a Checkout session's current state to the order. Idempotent —
        replayed webhooks and repeated syncs are no-ops. Returns True when
        the order changed.
        """
        payment_status = session.get('payment_status', '')
        session_status = session.get('status', '')
        # A pay-as-you-go plan charges nothing up front, so its completed
        # checkout reports no_payment_required rather than paid.
        settled = payment_status == 'paid' or (
            payment_status == 'no_payment_required' and session_status == 'complete'
        )

        if settled and order.status == Order.STATUS_PENDING:
            details = session.get('customer_details') or {}
            order.status = Order.STATUS_PAID
            order.paid_at = timezone.now()
            payment_intent = session.get('payment_intent')
            order.stripe_payment_intent_id = (
                payment_intent if isinstance(payment_intent, str)
                else (payment_intent or {}).get('id', '')
            )
            # Lowercase to match manually-entered CRM emails, which the
            # serializer normalizes the same way — otherwise a mixed-case
            # checkout email creates a duplicate Customer row.
            checkout_email = (details.get('email') or '').strip().lower()
            order.customer_email = checkout_email or order.customer_email
            order.customer_name = details.get('name') or ''
            amount_total = session.get('amount_total')
            if amount_total is not None:
                order.amount_total_cents = amount_total
            order.customer = self._upsert_customer(order, _id(session.get('customer')))
            order.save(update_fields=[
                'status', 'paid_at', 'stripe_payment_intent_id', 'customer',
                'customer_email', 'customer_name', 'amount_total_cents', 'updated_at',
            ])
            subscription_id = _id(session.get('subscription'))
            if subscription_id:
                self._record_checkout_subscription(order, session, subscription_id)
            return True

        if session_status == 'expired' and order.status == Order.STATUS_PENDING:
            order.status = Order.STATUS_CANCELED
            order.save(update_fields=['status', 'updated_at'])
            return True

        return False

    def _upsert_customer(self, order: Order, stripe_customer_id: str = ''):
        """Find or create the CRM customer for a paid order's email."""
        if not order.customer_email:
            return None
        customer, created = Customer.objects.get_or_create(
            project=self.project,
            email=order.customer_email,
            defaults={
                'name': order.customer_name,
                'source': 'checkout',
                'stripe_customer_id': stripe_customer_id,
            },
        )
        changed = []
        if not created and order.customer_name and not customer.name:
            customer.name = order.customer_name
            changed.append('name')
        if stripe_customer_id and customer.stripe_customer_id != stripe_customer_id:
            customer.stripe_customer_id = stripe_customer_id
            changed.append('stripe_customer_id')
        if changed:
            customer.save(update_fields=changed + ['updated_at'])
        return customer

    # -- subscriptions ---------------------------------------------------------

    def _record_checkout_subscription(self, order: Order, session, subscription_id: str):
        """Mirror the subscription a completed checkout started."""
        data = {'id': subscription_id, 'customer': session.get('customer'),
                'status': 'active', 'metadata': {}}
        try:
            data = self._client().retrieve_subscription(subscription_id)
        except (SellServiceError, StripeClientError):
            # The webhook brings the full details; record what we know now.
            logger.warning('Could not load subscription %s from Stripe', subscription_id)
        plan = next(
            (item.product for item in order.items.select_related('product')
             if item.product and item.product.is_recurring),
            None,
        )
        return self.upsert_subscription(data, product=plan, email=order.customer_email)

    def upsert_subscription(self, data, product: Product | None = None, email: str = ''):
        """Create or update the mirror of a Stripe subscription object."""
        subscription_id = data.get('id', '')
        if not subscription_id:
            return None
        stripe_customer_id = _id(data.get('customer'))
        metadata = data.get('metadata') or {}
        if product is None and metadata.get('imagi_product_id'):
            product = self.project.sell_products.filter(
                id=metadata.get('imagi_product_id')
            ).first()

        existing = self.project.sell_subscriptions.filter(
            stripe_subscription_id=subscription_id
        ).first()
        customer = None
        if stripe_customer_id:
            customer = self.project.sell_customers.filter(
                stripe_customer_id=stripe_customer_id
            ).first()
        if customer is None and email:
            customer = self.project.sell_customers.filter(email=email).first()
        if not email:
            email = (customer.email if customer else '') or (
                existing.customer_email if existing else ''
            )

        # Newer API versions keep the period on each item.
        period_end = data.get('current_period_end')
        if not period_end:
            items = ((data.get('items') or {}).get('data') or [])
            period_end = items[0].get('current_period_end') if items else None

        values = {
            'status': data.get('status') or 'incomplete',
            'cancel_at_period_end': bool(data.get('cancel_at_period_end')),
            'current_period_end': _ts(period_end),
        }
        if stripe_customer_id:
            values['stripe_customer_id'] = stripe_customer_id
        if customer:
            values['customer'] = customer
        if email:
            values['customer_email'] = email
        if product:
            values['product'] = product
            values['product_name'] = product.name

        if existing:
            for field, value in values.items():
                setattr(existing, field, value)
            existing.save()
            return existing
        try:
            with transaction.atomic():
                return Subscription.objects.create(
                    project=self.project,
                    stripe_subscription_id=subscription_id,
                    **values,
                )
        except IntegrityError:
            # A webhook and a status poll raced to create it.
            subscription = self.project.sell_subscriptions.get(
                stripe_subscription_id=subscription_id
            )
            for field, value in values.items():
                setattr(subscription, field, value)
            subscription.save()
            return subscription

    def active_subscriptions(self, email: str):
        email = (email or '').strip().lower()
        return self.project.sell_subscriptions.filter(
            customer_email=email,
            status__in=list(Subscription.ACTIVE_STATUSES),
        ).select_related('product')

    # -- pay as you go -----------------------------------------------------------

    def _usage_price_signature(self, product: Product) -> str:
        currency = (self.config.currency if self.config else '') or 'usd'
        return f'{currency}:{product.price_cents}:{product.usage_unit_count}:{product.usage_unit_label}'

    def ensure_usage_price(self, client: StripeClient, product: Product) -> str:
        """
        The Stripe meter and metered price a pay-as-you-go product bills
        through, created on the merchant's account the first time they're
        needed and replaced when the price changes. Returns the price id.
        """
        account_ref = self._account_ref()
        signature = self._usage_price_signature(product)
        if (
            product.stripe_price_id
            and product.stripe_price_signature == signature
            and product.stripe_account_ref == account_ref
        ):
            return product.stripe_price_id

        if product.stripe_account_ref != account_ref:
            product.stripe_meter_id = ''
        event_name = product.stripe_meter_event_name or f'imagi_p{self.project.id}_product_{product.id}'
        try:
            if not product.stripe_meter_id:
                meter = client.create_meter(
                    f'{product.name} ({product.usage_unit_label or "units"})', event_name
                )
                product.stripe_meter_id = meter.get('id', '')
            unit_amount = (
                Decimal(product.price_cents) / Decimal(max(product.usage_unit_count, 1))
            ).quantize(Decimal('0.000000000001')).normalize()
            price = client.create_metered_price(
                product.stripe_meter_id,
                (self.config.currency if self.config else '') or 'usd',
                format(unit_amount, 'f'),
                product.name,
                product.usage_unit_label,
            )
        except StripeClientError as exc:
            raise SellServiceError(f'Stripe could not set up the pay-as-you-go price: {exc}') from exc

        product.stripe_meter_event_name = event_name
        product.stripe_price_id = price.get('id', '')
        product.stripe_price_signature = signature
        product.stripe_account_ref = account_ref
        product.save(update_fields=[
            'stripe_meter_id', 'stripe_meter_event_name', 'stripe_price_id',
            'stripe_price_signature', 'stripe_account_ref', 'updated_at',
        ])
        return product.stripe_price_id

    def report_usage(self, email: str, quantity, idempotency_key: str = '',
                     product_id=None) -> UsageEvent:
        """
        Record usage for a customer's pay-as-you-go plan and send it to
        Stripe. Called by the business's own backend with its server key.
        A repeated idempotency key returns the first report unchanged.
        """
        email = (email or '').strip().lower()
        if not email:
            raise SellServiceError('Provide the customer\'s email.')
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            raise SellServiceError('quantity must be a whole number.')
        if not 1 <= quantity <= MAX_USAGE_QUANTITY:
            raise SellServiceError(f'quantity must be between 1 and {MAX_USAGE_QUANTITY:,}.')
        idempotency_key = (idempotency_key or '').strip()[:100]

        if idempotency_key:
            existing = self.project.sell_usage_events.filter(
                idempotency_key=idempotency_key
            ).first()
            if existing:
                return existing

        subscriptions = [s for s in self.active_subscriptions(email) if s.product and s.product.is_usage]
        if product_id is not None:
            subscriptions = [s for s in subscriptions if str(s.product_id) == str(product_id)]
        if not subscriptions:
            raise SellServiceError(
                'This customer has no active pay-as-you-go plan. Send them to '
                'your pricing page to subscribe first.'
            )
        subscription = subscriptions[0]
        product = subscription.product
        if not subscription.stripe_customer_id or not product.stripe_meter_event_name:
            raise SellServiceError('This subscription is missing its Stripe details.')

        client = self._client()
        if not idempotency_key:
            idempotency_key = f'auto-{timezone.now().timestamp()}-{subscription.id}'
        try:
            with transaction.atomic():
                event = UsageEvent.objects.create(
                    project=self.project,
                    subscription=subscription,
                    product=product,
                    customer_email=email,
                    quantity=quantity,
                    idempotency_key=idempotency_key,
                )
        except IntegrityError:
            return self.project.sell_usage_events.get(idempotency_key=idempotency_key)
        try:
            client.create_meter_event(
                product.stripe_meter_event_name,
                subscription.stripe_customer_id,
                quantity,
                identifier=f'imagi-{self.project.id}-{idempotency_key}',
            )
        except StripeClientError as exc:
            # Not counted: let the caller retry with the same key.
            event.delete()
            raise SellServiceError(f'Stripe did not accept the usage report: {exc}') from exc
        return event

    def sync_order(self, order: Order) -> bool:
        """
        Pull the order's session state from Stripe. The fallback when the
        webhook isn't configured or can't reach us (e.g. local dev).
        """
        if not order.stripe_checkout_session_id:
            raise SellServiceError('This order has no Stripe checkout session to sync.')
        client = self._client()
        try:
            session = client.retrieve_session(order.stripe_checkout_session_id)
        except StripeClientError as exc:
            raise SellServiceError(f'Stripe could not load the checkout session: {exc}') from exc
        return self.apply_session(order, session)

    def mark_fulfilled(self, order: Order) -> Order:
        if order.status != Order.STATUS_PAID:
            raise SellServiceError('Only paid orders can be marked fulfilled.')
        order.status = Order.STATUS_FULFILLED
        order.fulfilled_at = timezone.now()
        order.save(update_fields=['status', 'fulfilled_at', 'updated_at'])
        return order

    # -- webhooks ---------------------------------------------------------------

    def handle_webhook_event(self, event) -> bool:
        """
        Apply a verified Stripe event. Unknown event types are ignored.
        Returns True when an order was updated.
        """
        event_type = event.get('type', '')
        obj = (event.get('data') or {}).get('object') or {}

        if event_type in (
            'checkout.session.completed',
            'checkout.session.async_payment_succeeded',
            'checkout.session.expired',
        ):
            order = self._order_for_session(obj)
            if not order:
                return False
            return self.apply_session(order, obj)

        if event_type in (
            'customer.subscription.created',
            'customer.subscription.updated',
            'customer.subscription.deleted',
        ):
            return self.upsert_subscription(obj) is not None

        if event_type == 'charge.refunded':
            # Stripe fires charge.refunded for partial refunds too; the
            # charge's `refunded` flag is only true when the full amount came
            # back. Only a full refund should drop the order from revenue.
            if not obj.get('refunded'):
                return False
            payment_intent = obj.get('payment_intent') or ''
            if not payment_intent:
                return False
            order = self.project.sell_orders.filter(
                stripe_payment_intent_id=payment_intent,
                status__in=[Order.STATUS_PAID, Order.STATUS_FULFILLED],
            ).first()
            if not order:
                return False
            order.status = Order.STATUS_REFUNDED
            order.save(update_fields=['status', 'updated_at'])
            return True

        return False

    def _order_for_session(self, session) -> Order | None:
        session_id = session.get('id', '')
        order = None
        if session_id:
            order = self.project.sell_orders.filter(
                stripe_checkout_session_id=session_id,
            ).first()
        if not order:
            order_id = (session.get('metadata') or {}).get('imagi_order_id')
            if order_id:
                order = self.project.sell_orders.filter(id=order_id).first()
        return order
