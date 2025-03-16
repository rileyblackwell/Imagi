"""
Service for managing user credit balances.
"""

import logging
from decimal import Decimal
from django.db import transaction
from django.contrib.auth import get_user_model
from typing import Dict, Any, Union, Optional

from ..models import CreditBalance

User = get_user_model()
logger = logging.getLogger(__name__)

class CreditService:
    """Service for managing user credit balances."""
    
    def get_balance(self, user) -> float:
        """
        Get a user's credit balance.
        
        Args:
            user: The user
            
        Returns:
            The user's balance
        """
        balance, created = CreditBalance.objects.get_or_create(user=user)
        return float(balance.balance)
        
    def add_credits(self, user, amount: float, transaction_obj=None) -> Dict[str, Any]:
        """
        Add credits to a user's balance.
        
        Args:
            user: The user
            amount: The amount to add
            transaction_obj: Optional transaction object to update
            
        Returns:
            Dict with the new balance and success status
        """
        try:
            with transaction.atomic():
                balance, created = CreditBalance.objects.get_or_create(user=user)
                
                # Update balance
                balance.balance = Decimal(str(float(balance.balance) + amount))
                balance.save()
                
                # Update transaction if provided
                if transaction_obj:
                    transaction_obj.status = 'completed'
                    transaction_obj.save()
                
            return {
                'success': True,
                'new_balance': float(balance.balance),
                'credits_added': amount
            }
            
        except Exception as e:
            logger.error(f"Error adding credits: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
        
    def deduct_credits(self, user, amount: float, transaction_description: Optional[str] = None) -> Dict[str, Any]:
        """
        Deduct credits from a user's balance.
        
        Args:
            user: The user
            amount: The amount to deduct
            transaction_description: Optional description for the transaction
            
        Returns:
            Dict with the new balance and success status
        """
        try:
            if amount <= 0:
                raise ValueError("Amount must be positive")
                
            with transaction.atomic():
                try:
                    balance = CreditBalance.objects.select_for_update().get(user=user)
                except CreditBalance.DoesNotExist:
                    return {
                        'success': False,
                        'error': 'No credit balance found'
                    }
                
                # Check if user has sufficient credits
                if float(balance.balance) < amount:
                    return {
                        'success': False,
                        'error': 'Insufficient credits',
                        'current_balance': float(balance.balance),
                        'required_credits': amount
                    }
                    
                # Update balance
                balance.balance = Decimal(str(float(balance.balance) - amount))
                balance.save()
                
                # Create usage transaction
                if hasattr(self, 'transaction_service'):
                    transaction_description = transaction_description or f"Used {amount} credits"
                    self.transaction_service.create_usage_transaction(
                        user,
                        amount,
                        description=transaction_description
                    )
                
            return {
                'success': True,
                'new_balance': float(balance.balance),
                'credits_deducted': amount
            }
            
        except Exception as e:
            logger.error(f"Error deducting credits: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def check_credits(self, user, required_credits: float) -> Dict[str, Any]:
        """
        Check if a user has sufficient credits.
        
        Args:
            user: The user
            required_credits: The required credits
            
        Returns:
            Dict with the check result
        """
        try:
            current_balance = self.get_balance(user)
            
            has_sufficient = current_balance >= required_credits
            
            result = {
                'success': True,
                'has_sufficient': has_sufficient,
                'current_balance': current_balance,
                'required_credits': required_credits
            }
            
            # If insufficient, calculate how many more are needed
            if not has_sufficient:
                result['needed_credits'] = required_credits - current_balance
                
            return result
            
        except Exception as e:
            logger.error(f"Error checking credits: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            } 