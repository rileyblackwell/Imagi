"""
Service for managing user payment methods.
"""

import logging
from typing import Dict, Any, Optional

from ..models import PaymentMethod, StripeCustomer

logger = logging.getLogger(__name__)

class PaymentMethodService:
    """Service for managing user payment methods."""

    def get_stripe_customer_id(self, user) -> Optional[str]:
        """
        Get a user's Stripe customer ID.

        Args:
            user: The user

        Returns:
            The Stripe customer ID or None if not set
        """
        try:
            customer, _ = StripeCustomer.objects.get_or_create(user=user)
            return customer.stripe_customer_id or None

        except Exception as e:
            logger.error(f"Error getting Stripe customer ID: {str(e)}")
            return None

    def set_stripe_customer_id(self, user, customer_id: str) -> bool:
        """
        Set a user's Stripe customer ID.

        Args:
            user: The user
            customer_id: The Stripe customer ID

        Returns:
            True if successful, False otherwise
        """
        try:
            customer, _ = StripeCustomer.objects.get_or_create(user=user)
            customer.stripe_customer_id = customer_id
            customer.save(update_fields=['stripe_customer_id', 'last_updated'])
            return True

        except Exception as e:
            logger.error(f"Error setting Stripe customer ID: {str(e)}")
            return False
            
    def create_payment_method(self, user, payment_method_data: Dict[str, Any]) -> PaymentMethod:
        """
        Create a payment method record.
        
        Args:
            user: The user
            payment_method_data: The payment method data
                - payment_method_id: The Stripe payment method ID
                - card_brand: The card brand (e.g., 'visa')
                - last4: The last 4 digits of the card
                - exp_month: The expiration month
                - exp_year: The expiration year
                - is_default: Whether this is the default payment method
            
        Returns:
            The created payment method
        """
        try:
            # Check if this is the first payment method for the user
            is_first = not PaymentMethod.objects.filter(user=user).exists()
            
            # If is_default not specified, make it default if it's the first payment method
            if 'is_default' not in payment_method_data and is_first:
                payment_method_data['is_default'] = True
                
            payment_method = PaymentMethod.objects.create(
                user=user,
                **payment_method_data
            )
            
            return payment_method
            
        except Exception as e:
            logger.error(f"Error creating payment method: {str(e)}")
            raise
