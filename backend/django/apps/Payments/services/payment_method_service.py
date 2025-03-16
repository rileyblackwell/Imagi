"""
Service for managing user payment methods.
"""

import logging
from typing import Dict, Any, List, Optional
from django.db import transaction

from ..models import PaymentMethod

logger = logging.getLogger(__name__)

class PaymentMethodService:
    """Service for managing user payment methods."""
    
    def get_stripe_customer_id(self, user) -> Optional[str]:
        """
        Get a user's Stripe customer ID.
        
        Args:
            user: The user
            
        Returns:
            The Stripe customer ID or None if not found
        """
        try:
            if hasattr(user, 'profile') and user.profile.stripe_customer_id:
                return user.profile.stripe_customer_id
            return None
            
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
            user.profile.stripe_customer_id = customer_id
            user.profile.save()
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
            
    def get_payment_methods(self, user) -> List[PaymentMethod]:
        """
        Get a user's payment methods.
        
        Args:
            user: The user
            
        Returns:
            List of payment methods
        """
        try:
            return list(PaymentMethod.objects.filter(user=user).order_by('-is_default', '-created_at'))
            
        except Exception as e:
            logger.error(f"Error getting payment methods: {str(e)}")
            return []
            
    def get_default_payment_method(self, user) -> Optional[PaymentMethod]:
        """
        Get a user's default payment method.
        
        Args:
            user: The user
            
        Returns:
            The default payment method or None if not found
        """
        try:
            return PaymentMethod.objects.filter(user=user, is_default=True).first()
            
        except Exception as e:
            logger.error(f"Error getting default payment method: {str(e)}")
            return None
            
    def set_default_payment_method(self, user, payment_method_id: str) -> bool:
        """
        Set a payment method as the default.
        
        Args:
            user: The user
            payment_method_id: The payment method ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with transaction.atomic():
                # Clear existing default
                PaymentMethod.objects.filter(user=user, is_default=True).update(is_default=False)
                
                # Set new default
                method = PaymentMethod.objects.get(user=user, payment_method_id=payment_method_id)
                method.is_default = True
                method.save()
                
            return True
            
        except Exception as e:
            logger.error(f"Error setting default payment method: {str(e)}")
            return False
            
    def delete_payment_method(self, user, payment_method_id: str) -> bool:
        """
        Delete a payment method.
        
        Args:
            user: The user
            payment_method_id: The payment method ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            method = PaymentMethod.objects.get(user=user, payment_method_id=payment_method_id)
            
            # If this is the default method, find a new default
            if method.is_default:
                next_method = PaymentMethod.objects.filter(user=user).exclude(payment_method_id=payment_method_id).first()
                if next_method:
                    next_method.is_default = True
                    next_method.save()
                    
            method.delete()
            return True
            
        except PaymentMethod.DoesNotExist:
            return False
        except Exception as e:
            logger.error(f"Error deleting payment method: {str(e)}")
            return False 