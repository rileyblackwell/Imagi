"""
Service for managing user credit balances.
"""

import logging
from decimal import Decimal
from django.db import transaction
from django.contrib.auth import get_user_model
from typing import Dict, Any, Optional

from ..models import CreditBalance

User = get_user_model()
logger = logging.getLogger(__name__)

class CreditService:
    """Service for managing user credit balances."""
    
    def __init__(self):
        """Initialize the credit service."""
        # Lazy import to avoid circular imports
        from .transaction_service import TransactionService
        self.transaction_service = TransactionService()
    
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
            
            # Ensure precise decimal handling for small amounts
            amount_decimal = Decimal(str(float(amount)))
            
            # Log the precise amount being deducted
            logger.info(f"Deducting credits from user {user.username}: ${float(amount):.4f} ({amount_decimal})")
            
            with transaction.atomic():
                try:
                    balance = CreditBalance.objects.select_for_update().get(user=user)
                except CreditBalance.DoesNotExist:
                    # Create a new balance if it doesn't exist
                    balance = CreditBalance.objects.create(user=user, balance=0)
                    
                # Get the current balance as Decimal for precise calculation
                current_balance = Decimal(str(float(balance.balance)))
                logger.info(f"User {user.username} current balance: ${float(current_balance):.4f}")
                
                # Check if user has sufficient credits with epsilon for floating point precision
                epsilon = Decimal('0.0001')
                if current_balance + epsilon < amount_decimal:
                    logger.warning(f"Insufficient credits: {float(current_balance):.4f} < {float(amount):.4f}")
                    return {
                        'success': False,
                        'error': 'Insufficient credits',
                        'current_balance': float(current_balance),
                        'required_credits': float(amount_decimal)
                    }
                
                # Calculate new balance with precise decimal arithmetic
                new_balance = current_balance - amount_decimal
                logger.info(f"Calculated new balance: ${float(new_balance):.4f}")
                
                # Update balance - ensure we use exact decimal arithmetic
                balance.balance = new_balance
                balance.save()
                logger.info(f"Saved new balance for user {user.username}: ${float(balance.balance):.4f}")
                
                # Create usage transaction
                if hasattr(self, 'transaction_service') and self.transaction_service:
                    transaction_description = transaction_description or f"Used {float(amount):.4f} credits"
                    transaction_record = self.transaction_service.create_usage_transaction(
                        user,
                        amount,
                        description=transaction_description
                    )
                    logger.info(f"Created transaction record: {transaction_record and transaction_record.id}")
                else:
                    logger.warning(f"transaction_service not available in CreditService, transaction not recorded")
                
            # Refresh from database to get the final balance
            try:
                balance.refresh_from_db()
                final_balance = float(balance.balance)
                logger.info(f"Final balance after refresh: ${final_balance:.4f}")
            except Exception as refresh_error:
                logger.error(f"Error refreshing balance: {str(refresh_error)}")
                final_balance = float(new_balance)
            
            return {
                'success': True,
                'new_balance': final_balance,
                'credits_deducted': float(amount)
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
            
            # Add a small epsilon to handle floating point comparison
            epsilon = 0.0001
            has_sufficient = current_balance + epsilon >= required_credits
            
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