"""
Checkout and order workflows for the Sell app.

Wraps the raw StripeClient with everything project-specific: building
checkout sessions from the project's catalog, recording pending orders,
applying payment outcomes from webhooks (or a manual sync when webhooks
can't reach us), and upserting customers from completed checkouts.
"""

import logging

from django.conf import settings as django_settings
from django.db import transaction
from django.utils import timezone

from ..models import Customer, Order, OrderItem, Product
from .stripe_client import StripeClient, StripeClientError

logger = logging.getLogger(__name__)

# Guardrails for a single checkout session.
MAX_LINE_ITEMS = 20
MAX_QUANTITY = 100

# Stripe won't charge less than ~$0.50 (or equivalent) per session.
MIN_PRICE_CENTS = 50


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


def default_success_url(project_id: int) -> str:
    frontend = django_settings.FRONTEND_URL.rstrip('/')
    # Stripe substitutes the session id into the placeholder on redirect.
    return f'{frontend}/checkout/{project_id}/success?session_id={{CHECKOUT_SESSION_ID}}'


def default_cancel_url(project_id: int) -> str:
    frontend = django_settings.FRONTEND_URL.rstrip('/')
    return f'{frontend}/checkout/{project_id}/cancel'


class SellService:
    """Selling operations for a single project."""

    def __init__(self, project):
        self.project = project
        self.config = getattr(project, 'sell_settings', None)

    # -- setup ---------------------------------------------------------------

    def _client(self) -> StripeClient:
        if not self.config or not self.config.is_configured:
            raise SellServiceError(
                'Stripe is not connected. Add your Stripe secret key in '
                'Sell settings first.'
            )
        return StripeClient(self.config.stripe_secret_key)

    def verify(self) -> dict:
        """
        Check the stored secret key against Stripe and cache the account
        identity for display.
        """
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
        """
        client = self._client()
        customer_email = (customer_email or '').strip().lower()

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
        amount_total = sum(product.price_cents * quantity for product, quantity in resolved)

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

        try:
            session = client.create_checkout_session(
                line_items=line_items,
                success_url=success_url or default_success_url(self.project.id),
                cancel_url=cancel_url or default_cancel_url(self.project.id),
                metadata={
                    'imagi_project_id': str(self.project.id),
                    'imagi_order_id': str(order.id),
                },
                customer_email=customer_email,
                mode=mode,
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

        if payment_status == 'paid' and order.status == Order.STATUS_PENDING:
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
            order.customer = self._upsert_customer(order)
            order.save(update_fields=[
                'status', 'paid_at', 'stripe_payment_intent_id', 'customer',
                'customer_email', 'customer_name', 'amount_total_cents', 'updated_at',
            ])
            return True

        if session_status == 'expired' and order.status == Order.STATUS_PENDING:
            order.status = Order.STATUS_CANCELED
            order.save(update_fields=['status', 'updated_at'])
            return True

        return False

    def _upsert_customer(self, order: Order):
        """Find or create the CRM customer for a paid order's email."""
        if not order.customer_email:
            return None
        customer, created = Customer.objects.get_or_create(
            project=self.project,
            email=order.customer_email,
            defaults={'name': order.customer_name, 'source': 'checkout'},
        )
        if not created and order.customer_name and not customer.name:
            customer.name = order.customer_name
            customer.save(update_fields=['name', 'updated_at'])
        return customer

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
