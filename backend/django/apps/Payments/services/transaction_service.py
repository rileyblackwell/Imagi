"""
Read access to the historical transaction record.

Transactions were written by the prepaid-credit purchase flow, which no longer
exists — access is sold as subscription plans with a metered allowance. Nothing
creates transactions now; these methods only read what is already there so the
history pages keep working.
"""

import logging
from typing import Dict, Any
from django.db.models import QuerySet

from ..models import Transaction

logger = logging.getLogger(__name__)

class TransactionService:
    """Read-only access to historical payment transactions."""

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