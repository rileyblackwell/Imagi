"""
Thin wrapper around the Stripe SDK for the Sell app.

Every call passes its key via the `api_key` kwarg: the project's own secret
key, or, for a project connected through Stripe Connect, Imagi's platform key
together with `stripe_account` (the Stripe-Account header), which makes the
call on the connected account's behalf. Never set the module-global
`stripe.api_key` here — that one belongs to the platform's own billing
(apps.Payments) and per-project keys must not clobber it under concurrent
requests.
"""

import json
import logging

import stripe

logger = logging.getLogger(__name__)


class StripeClientError(Exception):
    """A Stripe API problem, with Stripe's user-facing message when available."""

    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code


def _wrap(exc: 'stripe.error.StripeError') -> StripeClientError:
    message = getattr(exc, 'user_message', None) or str(exc)
    return StripeClientError(message, code=getattr(exc, 'code', None))


def to_plain_dict(obj) -> dict:
    """
    Normalize a StripeObject to plain nested dicts. StripeObject only
    supports item access (no .get()), so the service layer works with
    plain dicts instead. StripeObject.__str__ is its JSON representation.
    """
    if isinstance(obj, dict) and type(obj) is dict:
        return obj
    return json.loads(str(obj))


class StripeClient:
    """Stripe operations on one merchant account."""

    def __init__(self, api_key: str, stripe_account: str = ''):
        self.api_key = api_key
        self.stripe_account = stripe_account

    def _auth(self) -> dict:
        auth = {'api_key': self.api_key}
        if self.stripe_account:
            auth['stripe_account'] = self.stripe_account
        return auth

    def _call(self, fn, *args, **params):
        try:
            return to_plain_dict(fn(*args, **params, **self._auth()))
        except stripe.error.StripeError as exc:
            raise _wrap(exc) from exc

    def fetch_account(self) -> dict:
        """The merchant account (used to verify credentials)."""
        if self.stripe_account:
            return self._call_platform(stripe.Account.retrieve, self.stripe_account)
        try:
            return to_plain_dict(stripe.Account.retrieve(api_key=self.api_key))
        except stripe.error.StripeError as exc:
            raise _wrap(exc) from exc

    def _call_platform(self, fn, *args, **params):
        """A call made as the platform itself (no Stripe-Account header)."""
        try:
            return to_plain_dict(fn(*args, api_key=self.api_key, **params))
        except stripe.error.StripeError as exc:
            raise _wrap(exc) from exc

    # -- Stripe Connect (platform calls) ---------------------------------------

    def create_connected_account(self, email: str = '', metadata: dict | None = None) -> dict:
        """
        A connected account the business owns outright: full Stripe
        Dashboard, Stripe collects its fees and covers its losses. That is a
        Standard account in Stripe's older terms; payments on it are direct
        charges, so the business is the merchant of record.
        """
        params = {
            'controller': {
                'stripe_dashboard': {'type': 'full'},
                'fees': {'payer': 'account'},
                'losses': {'payments': 'stripe'},
                'requirement_collection': 'stripe',
            },
            'metadata': metadata or {},
        }
        if email:
            params['email'] = email
        return self._call_platform(stripe.Account.create, **params)

    def create_onboarding_link(self, account_id: str, refresh_url: str, return_url: str) -> dict:
        """Stripe-hosted sign-up for the connected account (single use, expires)."""
        return self._call_platform(
            stripe.AccountLink.create,
            account=account_id,
            refresh_url=refresh_url,
            return_url=return_url,
            type='account_onboarding',
        )

    # -- Pay as you go (Billing meters) -----------------------------------------

    def create_meter(self, display_name: str, event_name: str) -> dict:
        """A meter that sums the `value` of events keyed by Stripe customer id."""
        return self._call(
            stripe.billing.Meter.create,
            display_name=display_name[:250],
            event_name=event_name,
            default_aggregation={'formula': 'sum'},
            customer_mapping={'type': 'by_id', 'event_payload_key': 'stripe_customer_id'},
            value_settings={'event_payload_key': 'value'},
        )

    def create_metered_price(self, meter_id: str, currency: str, unit_amount_decimal: str,
                             product_name: str, unit_label: str = '') -> dict:
        product_data = {'name': product_name[:250]}
        if unit_label:
            product_data['unit_label'] = unit_label[:12]
        return self._call(
            stripe.Price.create,
            currency=currency,
            unit_amount_decimal=unit_amount_decimal,
            recurring={'interval': 'month', 'usage_type': 'metered', 'meter': meter_id},
            product_data=product_data,
        )

    def create_meter_event(self, event_name: str, stripe_customer_id: str,
                           value: int, identifier: str) -> dict:
        return self._call(
            stripe.billing.MeterEvent.create,
            event_name=event_name,
            payload={'stripe_customer_id': stripe_customer_id, 'value': str(value)},
            identifier=identifier,
        )

    def retrieve_subscription(self, subscription_id: str) -> dict:
        return self._call(stripe.Subscription.retrieve, subscription_id)

    def create_checkout_session(self, line_items: list, success_url: str,
                                cancel_url: str, metadata: dict,
                                customer_email: str = '', mode: str = 'payment',
                                subscription_metadata: dict | None = None):
        """
        Create a hosted Stripe Checkout session. `mode` is 'payment' for
        one-time carts or 'subscription' when any line item recurs.
        """
        params = {
            'mode': mode,
            'line_items': line_items,
            'success_url': success_url,
            'cancel_url': cancel_url,
            'metadata': metadata,
        }
        if customer_email:
            params['customer_email'] = customer_email
        if subscription_metadata:
            params['subscription_data'] = {'metadata': subscription_metadata}
        if mode == 'payment':
            # A Stripe customer for one-time buyers too, so a later
            # subscription or usage report finds the same customer.
            params['customer_creation'] = 'always'
        return self._call(stripe.checkout.Session.create, **params)

    def retrieve_session(self, session_id: str) -> dict:
        return self._call(stripe.checkout.Session.retrieve, session_id)


def construct_webhook_event(payload: bytes, signature: str, webhook_secret: str) -> dict:
    """
    Verify and parse a Stripe webhook payload into plain dicts. Raises
    ValueError on a bad payload and stripe.error.SignatureVerificationError
    on a bad signature.
    """
    event = stripe.Webhook.construct_event(payload, signature, webhook_secret)
    return to_plain_dict(event)
