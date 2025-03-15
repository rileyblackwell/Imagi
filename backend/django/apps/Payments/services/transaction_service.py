"""
Service for managing payment transactions.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from django.db.models import QuerySet
from django.db import transaction

from ..models import Transaction, CreditPackage, CreditPlan

logger = logging.getLogger(__name__)

class TransactionService:
    """Service for managing payment transactions."""
    
    def create_purchase_transaction(self, user, amount: float, stripe_payment_intent_id: str = None,
                                   stripe_checkout_session_id: str = None, description: str = None) -> Transaction:
        """
        Create a purchase transaction.
        
        Args:
            user: The user making the purchase
            amount: The amount in credits
            stripe_payment_intent_id: Optional Stripe payment intent ID
            stripe_checkout_session_id: Optional Stripe checkout session ID
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
                stripe_checkout_session_id=stripe_checkout_session_id,
                description=transaction_description
            )
            
            return transaction
            
        except Exception as e:
            logger.error(f"Error creating purchase transaction: {str(e)}")
            raise
            
    def get_transaction_by_payment_intent(self, user, payment_intent_id: str) -> Optional[Transaction]:
        """
        Get a transaction by Stripe payment intent ID.
        
        Args:
            user: The user
            payment_intent_id: The Stripe payment intent ID
            
        Returns:
            The transaction or None if not found
        """
        try:
            return Transaction.objects.filter(
                user=user,
                stripe_payment_intent_id=payment_intent_id
            ).first()
            
        except Exception as e:
            logger.error(f"Error getting transaction by payment intent: {str(e)}")
            return None
            
    def get_transaction_by_checkout_session(self, session_id: str) -> Optional[Transaction]:
        """
        Get a transaction by Stripe checkout session ID.
        
        Args:
            session_id: The Stripe checkout session ID
            
        Returns:
            The transaction or None if not found
        """
        try:
            return Transaction.objects.filter(
                stripe_checkout_session_id=session_id
            ).first()
            
        except Exception as e:
            logger.error(f"Error getting transaction by checkout session: {str(e)}")
            return None
            
    def mark_transaction_completed(self, transaction_obj: Transaction) -> bool:
        """
        Mark a transaction as completed.
        
        Args:
            transaction_obj: The transaction to update
            
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
        Get a user's payment history.
        
        Args:
            user: The user
            limit: Optional limit on number of transactions to retrieve
            
        Returns:
            QuerySet of transactions
        """
        try:
            queryset = Transaction.objects.filter(
                user=user,
                transaction_type='purchase'
            ).order_by('-created_at')
            
            if limit:
                queryset = queryset[:limit]
                
            return queryset
            
        except Exception as e:
            logger.error(f"Error getting payment history: {str(e)}")
            return Transaction.objects.none()
            
    def get_transactions(self, user, status: str = None, sort_by: str = 'created_at', 
                        sort_order: str = 'desc') -> Dict[str, Any]:
        """
        Get a user's transactions with filtering and sorting.
        
        Args:
            user: The user
            status: Optional filter by status
            sort_by: Field to sort by
            sort_order: 'asc' or 'desc'
            
        Returns:
            Dict with transactions and count
        """
        try:
            queryset = Transaction.objects.filter(user=user)
            
            # Apply status filter
            if status:
                queryset = queryset.filter(status=status)
                
            # Validate sort_by field
            valid_sort_fields = ['created_at', 'amount', 'status']
            if sort_by not in valid_sort_fields:
                sort_by = 'created_at'
                
            # Apply sorting
            order_prefix = '-' if sort_order.lower() == 'desc' else ''
            queryset = queryset.order_by(f'{order_prefix}{sort_by}')
            
            return {
                'success': True,
                'transactions': queryset,
                'total_count': queryset.count()
            }
            
        except Exception as e:
            logger.error(f"Error getting transactions: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'transactions': [],
                'total_count': 0
            }
    
    def get_credit_packages(self, include_inactive: bool = False) -> List[CreditPackage]:
        """
        Get all credit packages.
        
        Args:
            include_inactive: Whether to include inactive packages
            
        Returns:
            List of credit packages
        """
        try:
            if include_inactive:
                return CreditPackage.objects.all()
            else:
                return CreditPackage.objects.filter(is_active=True)
                
        except Exception as e:
            logger.error(f"Error getting credit packages: {str(e)}")
            return []
    
    def get_credit_plans(self, include_inactive: bool = False) -> List[CreditPlan]:
        """
        Get all credit plans.
        
        Args:
            include_inactive: Whether to include inactive plans
            
        Returns:
            List of credit plans
        """
        try:
            if include_inactive:
                return CreditPlan.objects.all()
            else:
                return CreditPlan.objects.filter(is_active=True)
                
        except Exception as e:
            logger.error(f"Error getting credit plans: {str(e)}")
            return []
            
    def get_plan_by_id(self, plan_id: str) -> Optional[CreditPlan]:
        """
        Get a credit plan by ID.
        
        Args:
            plan_id: The plan ID
            
        Returns:
            The credit plan or None if not found
        """
        try:
            return CreditPlan.objects.filter(id=plan_id).first()
            
        except Exception as e:
            logger.error(f"Error getting plan by ID: {str(e)}")
            return None 