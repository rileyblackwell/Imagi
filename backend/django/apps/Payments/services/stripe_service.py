"""
Service for interacting with the Stripe API.
"""

import stripe
import logging
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Subscription statuses that still bill the customer. A second subscription
# alongside any of these would charge them twice.
LIVE_SUBSCRIPTION_STATUSES = ('active', 'trialing', 'past_due')


def to_plain_dict(obj):
    """Normalize a StripeObject to plain nested dicts; anything else passes through.

    Since stripe-python 13, StripeObject is no longer a dict subclass: it has
    item access but no .get(), so code written against dicts raises
    AttributeError on a real API response (mocked dicts in tests never show
    it). Everything this app reads off a subscription goes through here first.
    """
    if isinstance(obj, stripe.StripeObject):
        return obj.to_dict()
    return obj


class StripeService:
    """Service for interacting with Stripe API."""
    
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
    def create_customer(self, email: str, name: str, metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Create a Stripe customer.
        
        Args:
            email: Customer email
            name: Customer name
            metadata: Additional metadata for the customer
            
        Returns:
            The created customer
        """
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {}
            )
            
            return customer
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating customer: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error creating customer: {str(e)}")
            raise
    
    def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """
        Retrieve a customer by ID.
        
        Args:
            customer_id: The Stripe customer ID
            
        Returns:
            The customer
        """
        try:
            customer = stripe.Customer.retrieve(customer_id)
            return customer
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving customer: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error retrieving customer: {str(e)}")
            raise
    
    def list_payment_methods(self, customer_id: str, type: str = 'card') -> list:
        """
        List payment methods for a customer.
        
        Args:
            customer_id: The Stripe customer ID
            type: The payment method type (default: 'card')
            
        Returns:
            List of payment methods
        """
        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type=type
            )
            
            return payment_methods.data
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error listing payment methods: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error listing payment methods: {str(e)}")
            raise
    
    def attach_payment_method(self, payment_method_id: str, customer_id: str) -> Dict[str, Any]:
        """
        Attach a payment method to a customer.
        
        Args:
            payment_method_id: The Stripe payment method ID
            customer_id: The Stripe customer ID
            
        Returns:
            The attached payment method
        """
        try:
            payment_method = stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer_id
            )
            
            return payment_method
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error attaching payment method: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error attaching payment method: {str(e)}")
            raise
    
    def create_checkout_session(self, line_items: list, metadata: Dict[str, str],
                                success_url: str, cancel_url: str,
                                mode: str = 'subscription', customer: Optional[str] = None,
                                subscription_metadata: Optional[Dict[str, str]] = None) -> Any:
        """
        Create a Stripe Checkout Session.

        Args:
            line_items: List of line item dicts with price and quantity
            metadata: Session metadata
            success_url: URL to redirect on success
            cancel_url: URL to redirect on cancel
            mode: Checkout mode; only 'subscription' is used
            customer: Stripe customer ID (required for subscription mode)
            subscription_metadata: Metadata copied onto the subscription the
                session creates (session metadata stays on the session only)
        """
        try:
            params = {
                'line_items': line_items,
                'metadata': metadata,
                'success_url': success_url,
                'cancel_url': cancel_url,
                'mode': mode,
            }
            if customer:
                params['customer'] = customer
            if subscription_metadata:
                params['subscription_data'] = {'metadata': subscription_metadata}

            session = stripe.checkout.Session.create(**params)
            return session
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating checkout session: {str(e)}")
            raise

    def get_session_status(self, session_id: str) -> Any:
        """
        Retrieve a Checkout Session by ID.

        Args:
            session_id: The Stripe Checkout Session ID
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return session
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving session: {str(e)}")
            raise

    def create_portal_session(self, customer_id: str, return_url: str) -> Any:
        """
        Create a Stripe Billing Portal session for subscription management.

        Args:
            customer_id: The Stripe customer ID
            return_url: URL to redirect after portal session
        """
        try:
            portal_session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            return portal_session
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating portal session: {str(e)}")
            raise

    def list_live_subscriptions(self, customer_id: str) -> list:
        """
        The customer's subscriptions that are still billing, newest first.

        'active' and 'trialing' are in good standing; 'past_due' is still
        live too — Stripe is retrying its charge and will keep invoicing — so
        it counts when deciding whether a second subscription would double
        bill.
        """
        try:
            subscriptions = stripe.Subscription.list(
                customer=customer_id, status='all', limit=20
            )
            live = [
                sub for sub in (to_plain_dict(s) for s in subscriptions.data)
                if sub.get('status') in LIVE_SUBSCRIPTION_STATUSES
            ]
            return sorted(live, key=lambda sub: sub.get('created') or 0, reverse=True)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error listing subscriptions: {str(e)}")
            raise

    def change_subscription_price(self, subscription: Any, price_id: str) -> Any:
        """
        Move a subscription onto a different price, in place.

        The one line item is swapped rather than a second subscription being
        created, so the customer is only ever billed once. The prorated
        difference is invoiced immediately (always_invoice), and with
        pending_if_incomplete the switch only takes effect once that invoice
        is paid — an upgrade whose charge fails leaves the old plan in place
        instead of granting the bigger allowance unpaid.
        """
        items = (subscription.get('items') or {}).get('data') or []
        if len(items) != 1:
            raise ValueError(
                f"Subscription {subscription.get('id')} has {len(items)} items; expected 1"
            )
        try:
            return to_plain_dict(stripe.Subscription.modify(
                subscription['id'],
                items=[{'id': items[0]['id'], 'price': price_id}],
                proration_behavior='always_invoice',
                payment_behavior='pending_if_incomplete',
            ))
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error changing subscription price: {str(e)}")
            raise

    def cancel_subscription(self, subscription_id: str) -> Any:
        """Cancel a subscription now, crediting its unused time."""
        try:
            return stripe.Subscription.cancel(subscription_id, prorate=True)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error cancelling subscription: {str(e)}")
            raise

    def verify_webhook_event(self, payload: bytes, signature: str, webhook_secret: str) -> Dict[str, Any]:
        """
        Verify a webhook event from Stripe.
        
        Args:
            payload: The webhook payload
            signature: The webhook signature
            webhook_secret: The webhook secret
            
        Returns:
            The verified event

        Raises:
            ImproperlyConfigured: when no signing secret is configured. Stripe's
                library HMACs with whatever key it is given, including a
                zero-length one, so an unset STRIPE_WEBHOOK_SECRET would leave
                the signature computable by anyone — and this is the only path
                that writes Subscription rows. Fail closed instead.
        """
        if not webhook_secret:
            logger.error("STRIPE_WEBHOOK_SECRET is not configured - refusing to verify webhook")
            raise ImproperlyConfigured(
                "STRIPE_WEBHOOK_SECRET is not set; webhook signatures cannot be verified."
            )

        try:
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            
            return event
            
        except ValueError as e:
            logger.error(f"Invalid webhook payload: {str(e)}")
            raise
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error verifying webhook: {str(e)}")
            raise 