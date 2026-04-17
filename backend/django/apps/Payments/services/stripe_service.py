"""
Service for interacting with the Stripe API.
"""

import stripe
import logging
from django.conf import settings
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class StripeService:
    """Service for interacting with Stripe API."""
    
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
    def create_direct_payment(self, amount: float, payment_method_id: str, 
                         metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Create and confirm a payment intent with a specific payment method.
        
        Args:
            amount: The payment amount in dollars
            payment_method_id: The Stripe payment method ID
            metadata: Additional metadata for the payment intent
            
        Returns:
            The created and confirmed payment intent
        """
        try:
            # Convert amount to cents for Stripe
            amount_cents = int(amount * 100)
            
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency='usd',
                payment_method=payment_method_id,
                metadata=metadata or {},
                confirm=True,
                return_url=f"{settings.FRONTEND_URL}/payments/confirm",
            )
            
            return intent
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating direct payment: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error creating direct payment: {str(e)}")
            raise
    
    def get_payment_intent(self, payment_intent_id: str) -> Dict[str, Any]:
        """
        Retrieve a payment intent by ID.
        
        Args:
            payment_intent_id: The Stripe payment intent ID
            
        Returns:
            The payment intent
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return intent
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving payment intent: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error retrieving payment intent: {str(e)}")
            raise
    
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
                                mode: str = 'payment', customer: Optional[str] = None) -> Any:
        """
        Create a Stripe Checkout Session.

        Args:
            line_items: List of line item dicts with price and quantity
            metadata: Session metadata
            success_url: URL to redirect on success
            cancel_url: URL to redirect on cancel
            mode: 'payment' for one-time, 'subscription' for recurring
            customer: Stripe customer ID (required for subscription mode)
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

            session = stripe.checkout.Session.create(**params)
            return session
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating checkout session: {str(e)}")
            raise

    def create_price(self, unit_amount: int, metadata: Optional[Dict[str, str]] = None,
                     currency: str = 'usd') -> Any:
        """
        Create a one-time Stripe Price on the fly (for on-demand purchases).

        Args:
            unit_amount: Price in cents
            metadata: Additional metadata
            currency: Currency code
        """
        try:
            price = stripe.Price.create(
                unit_amount=unit_amount,
                currency=currency,
                product_data={'name': 'Imagi Credits'},
                metadata=metadata or {},
            )
            return price
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating price: {str(e)}")
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

    def list_plans(self) -> list:
        """List active recurring prices."""
        try:
            prices = stripe.Price.list(active=True, type='recurring')
            return prices.data
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error listing plans: {str(e)}")
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

    def verify_webhook_event(self, payload: bytes, signature: str, webhook_secret: str) -> Dict[str, Any]:
        """
        Verify a webhook event from Stripe.
        
        Args:
            payload: The webhook payload
            signature: The webhook signature
            webhook_secret: The webhook secret
            
        Returns:
            The verified event
        """
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