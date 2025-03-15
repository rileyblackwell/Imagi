"""
Service for managing user credit balances.
"""

import logging
from decimal import Decimal
from django.db import transaction
from django.contrib.auth import get_user_model
from typing import Dict, Any, Union, Optional

from ..models import CreditBalance, CreditPlan

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
                
                # Create usage transaction
                from ..models import Transaction
                Transaction.objects.create(
                    user=user,
                    amount=-amount,
                    transaction_type='usage',
                    status='completed',
                    description=transaction_description or f"Usage of {amount} credits"
                )
                
                # Update balance
                balance.balance = Decimal(str(float(balance.balance) - amount))
                balance.save()
                
            return {
                'success': True,
                'new_balance': float(balance.balance),
                'credits_deducted': amount
            }
            
        except ValueError as e:
            return {
                'success': False,
                'error': str(e)
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
            required_credits: The amount of credits required
            
        Returns:
            Dict with sufficient status and balance info
        """
        try:
            if required_credits <= 0:
                return {
                    'success': False,
                    'error': 'Invalid credit amount'
                }
            
            balance, created = CreditBalance.objects.get_or_create(user=user)
            has_sufficient_credits = float(balance.balance) >= required_credits
            
            result = {
                'success': True,
                'has_sufficient_credits': has_sufficient_credits,
                'current_balance': float(balance.balance),
                'required_credits': required_credits
            }
            
            if not has_sufficient_credits:
                # Get the smallest plan that covers the required credits
                plan = CreditPlan.objects.filter(
                    credits__gte=required_credits,
                    is_active=True
                ).order_by('credits').first()
                
                if plan:
                    from ..api.serializers import CreditPlanSerializer
                    result['suggested_plan'] = CreditPlanSerializer(plan).data
            
            return result
            
        except Exception as e:
            logger.error(f"Error checking credits: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            } 