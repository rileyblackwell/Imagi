"""
Service for managing payment transactions.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from django.db.models import QuerySet
from django.db import transaction

from ..models import Transaction, CreditPackage

logger = logging.getLogger(__name__)

class TransactionService:
    """Service for managing payment transactions."""
    
    def create_purchase_transaction(self, user, amount: float, stripe_payment_intent_id: str = None,
                                   description: str = None) -> Transaction:
        """
        Create a purchase transaction.
        
        Args:
            user: The user making the purchase
            amount: The amount in credits
            stripe_payment_intent_id: Optional Stripe payment intent ID
            description: Optional transaction description
            
        Returns:
            The created transaction
        """
        try:
            transaction_description = description or f"Purchase of {amount} credits"
            
            transaction = Transaction.objects.create(
                user=user,
                amount=amount,
                transaction_type='purchase',
                status='pending',
                stripe_payment_intent_id=stripe_payment_intent_id,
                description=transaction_description
            )
            
            return transaction
            
        except Exception as e:
            logger.error(f"Error creating purchase transaction: {str(e)}")
            raise
            
    def get_transaction_by_payment_intent(self, user, payment_intent_id: str) -> Optional[Transaction]:
        """
        Get a transaction by payment intent ID.
        
        Args:
            user: The user (optional, can be None to search across all users)
            payment_intent_id: The Stripe payment intent ID
            
        Returns:
            The transaction if found, None otherwise
        """
        try:
            query = {'stripe_payment_intent_id': payment_intent_id}
            if user:
                query['user'] = user
                
            return Transaction.objects.filter(**query).first()
            
        except Exception as e:
            logger.error(f"Error getting transaction by payment intent: {str(e)}")
            return None
            
    def mark_transaction_completed(self, transaction_obj: Transaction) -> bool:
        """
        Mark a transaction as completed.
        
        Args:
            transaction_obj: The transaction to mark as completed
            
        Returns:
            True if successful, False otherwise
        """
        try:
            transaction_obj.status = 'completed'
            transaction_obj.save()
            return True
            
        except Exception as e:
            logger.error(f"Error marking transaction completed: {str(e)}")
            return False
            
    def get_payment_history(self, user, limit: int = None) -> QuerySet:
        """
        Get payment history for a user.
        
        Args:
            user: The user
            limit: Optional limit on number of results
            
        Returns:
            QuerySet of transactions
        """
        try:
            query = Transaction.objects.filter(
                user=user,
                transaction_type='purchase',
                status='completed'
            ).order_by('-created_at')
            
            if limit:
                query = query[:limit]
                
            return query
            
        except Exception as e:
            logger.error(f"Error getting payment history: {str(e)}")
            return Transaction.objects.none()
            
    def get_transactions(self, user, status: str = None, sort_by: str = 'created_at', 
                        sort_order: str = 'desc') -> Dict[str, Any]:
        """
        Get transactions for a user with optional filtering and sorting.
        
        Args:
            user: The user
            status: Optional status filter
            sort_by: Field to sort by (default: 'created_at')
            sort_order: Sort order ('asc' or 'desc', default: 'desc')
            
        Returns:
            Dict with transactions and count
        """
        try:
            query = {'user': user}
            
            if status:
                query['status'] = status
                
            # Validate sort field
            valid_sort_fields = ['created_at', 'amount', 'status', 'transaction_type']
            if sort_by not in valid_sort_fields:
                sort_by = 'created_at'
                
            # Apply sort order
            order_prefix = '-' if sort_order.lower() == 'desc' else ''
            order_by = f"{order_prefix}{sort_by}"
            
            transactions = Transaction.objects.filter(**query).order_by(order_by)
            
            return {
                'transactions': transactions,
                'count': transactions.count()
            }
            
        except Exception as e:
            logger.error(f"Error getting transactions: {str(e)}")
            return {
                'transactions': Transaction.objects.none(),
                'count': 0
            }
            
    def get_credit_packages(self, include_inactive: bool = False) -> List[CreditPackage]:
        """
        Get available credit packages.
        
        Args:
            include_inactive: Whether to include inactive packages
            
        Returns:
            List of credit packages
        """
        try:
            query = {}
            if not include_inactive:
                query['is_active'] = True
                
            return list(CreditPackage.objects.filter(**query).order_by('amount'))
            
        except Exception as e:
            logger.error(f"Error getting credit packages: {str(e)}")
            return [] 