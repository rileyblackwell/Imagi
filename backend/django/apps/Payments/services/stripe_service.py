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
        # Get product ID from settings, use a default if not available
        self.product_id = getattr(settings, 'STRIPE_PRODUCT_ID', None)
        
    def create_payment_intent(self, amount: float, metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Create a Stripe PaymentIntent.
        
        Args:
            amount: The payment amount in dollars
            metadata: Additional metadata for the payment intent
            
        Returns:
            The created payment intent
        """
        try:
            # Convert amount to cents for Stripe
            amount_cents = int(amount * 100)
            
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency='usd',
                metadata=metadata or {},
                automatic_payment_methods={
                    'enabled': True,
                }
            )
            
            return intent
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating payment intent: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error creating payment intent: {str(e)}")
            raise
            
    def create_direct_payment(self, amount: float, payment_method_id: str, 
                             metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Create and confirm a payment intent directly using a payment method.
        
        Args:
            amount: The payment amount in dollars
            payment_method_id: The Stripe payment method ID
            metadata: Additional metadata for the payment intent
            
        Returns:
            The created and confirmed payment intent
        """
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),
                currency='usd',
                payment_method=payment_method_id,
                confirm=True,
                metadata=metadata or {}
            )
            
            return intent
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error processing direct payment: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error processing direct payment: {str(e)}")
            raise
            
    def confirm_payment(self, payment_intent_id: str) -> Dict[str, Any]:
        """
        Confirm a payment intent.
        
        Args:
            payment_intent_id: The Stripe payment intent ID
            
        Returns:
            The confirmed payment intent
        """
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return payment_intent
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error confirming payment: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error confirming payment: {str(e)}")
            raise
            
    def get_payment_intent(self, payment_intent_id: str) -> Dict[str, Any]:
        """
        Retrieve a payment intent.
        
        Args:
            payment_intent_id: The Stripe payment intent ID
            
        Returns:
            The payment intent
        """
        try:
            return stripe.PaymentIntent.retrieve(payment_intent_id)
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving payment intent: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error retrieving payment intent: {str(e)}")
            raise
    
    def create_checkout_session(self, line_items: list, metadata: dict, 
                               success_url: str, cancel_url: str) -> Dict[str, Any]:
        """
        Create a Stripe Checkout Session.
        
        Args:
            line_items: The line items for the checkout session
            metadata: Additional metadata for the checkout session
            success_url: The URL to redirect to after successful payment
            cancel_url: The URL to redirect to if payment is cancelled
            
        Returns:
            The created checkout session
        """
        try:
            checkout_session = stripe.checkout.Session.create(
                success_url=success_url,
                cancel_url=cancel_url,
                mode='payment',
                line_items=line_items,
                metadata=metadata
            )
            
            return checkout_session
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating checkout session: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error creating checkout session: {str(e)}")
            raise
            
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieve a checkout session.
        
        Args:
            session_id: The Stripe checkout session ID
            
        Returns:
            The checkout session
        """
        try:
            return stripe.checkout.Session.retrieve(session_id)
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving checkout session: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error retrieving checkout session: {str(e)}")
            raise
            
    def create_customer(self, email: str, name: str, metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Create a Stripe customer.
        
        Args:
            email: The customer's email
            name: The customer's name
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
        Retrieve a Stripe customer.
        
        Args:
            customer_id: The Stripe customer ID
            
        Returns:
            The customer
        """
        try:
            return stripe.Customer.retrieve(customer_id)
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving customer: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error retrieving customer: {str(e)}")
            raise
            
    def list_payment_methods(self, customer_id: str, type: str = 'card') -> list:
        """
        List a customer's payment methods.
        
        Args:
            customer_id: The Stripe customer ID
            type: The payment method type (default: 'card')
            
        Returns:
            The payment methods
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
            
    def create_price(self, unit_amount: int, currency: str = 'usd', 
                    metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Create a Stripe price.
        
        Args:
            unit_amount: The price amount in cents
            currency: The currency (default: 'usd')
            metadata: Additional metadata for the price
            
        Returns:
            The created price
        """
        try:
            if not self.product_id:
                raise ValueError("STRIPE_PRODUCT_ID setting is not configured")
                
            price = stripe.Price.create(
                unit_amount=unit_amount,
                currency=currency,
                product=self.product_id,
                metadata=metadata or {}
            )
            
            return price
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating price: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error creating price: {str(e)}")
            raise
            
    def list_plans(self) -> list:
        """
        List all active recurring prices (plans) for the product.
        
        Returns:
            The prices
        """
        try:
            if not self.product_id:
                logger.warning("STRIPE_PRODUCT_ID setting is not configured, returning empty plans list")
                return []
                
            plans = stripe.Price.list(
                product=self.product_id,
                active=True,
                type='recurring'
            )
            
            return plans.data
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error listing plans: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error listing plans: {str(e)}")
            raise
            
    def verify_webhook_event(self, payload: bytes, signature: str, webhook_secret: str) -> Dict[str, Any]:
        """
        Verify a webhook event.
        
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