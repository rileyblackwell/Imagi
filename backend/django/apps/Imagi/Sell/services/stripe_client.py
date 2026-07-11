"""
Thin wrapper around the Stripe SDK for the Sell app.

Every call passes the project's own secret key via the `api_key` kwarg.
Never set the module-global `stripe.api_key` here — that one belongs to the
platform's own billing (apps.Payments) and per-project keys must not clobber
it under concurrent requests.
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
    """Stripe operations authenticated with a single project's secret key."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def fetch_account(self) -> dict:
        """The account the key belongs to (used to verify credentials)."""
        try:
            return to_plain_dict(stripe.Account.retrieve(api_key=self.api_key))
        except stripe.error.StripeError as exc:
            raise _wrap(exc) from exc

    def create_checkout_session(self, line_items: list, success_url: str,
                                cancel_url: str, metadata: dict,
                                customer_email: str = ''):
        """Create a hosted Stripe Checkout session for a one-time payment."""
        params = {
            'mode': 'payment',
            'line_items': line_items,
            'success_url': success_url,
            'cancel_url': cancel_url,
            'metadata': metadata,
        }
        if customer_email:
            params['customer_email'] = customer_email
        try:
            return to_plain_dict(
                stripe.checkout.Session.create(api_key=self.api_key, **params)
            )
        except stripe.error.StripeError as exc:
            raise _wrap(exc) from exc

    def retrieve_session(self, session_id: str) -> dict:
        try:
            return to_plain_dict(
                stripe.checkout.Session.retrieve(session_id, api_key=self.api_key)
            )
        except stripe.error.StripeError as exc:
            raise _wrap(exc) from exc


def construct_webhook_event(payload: bytes, signature: str, webhook_secret: str) -> dict:
    """
    Verify and parse a Stripe webhook payload into plain dicts. Raises
    ValueError on a bad payload and stripe.error.SignatureVerificationError
    on a bad signature.
    """
    event = stripe.Webhook.construct_event(payload, signature, webhook_secret)
    return to_plain_dict(event)
