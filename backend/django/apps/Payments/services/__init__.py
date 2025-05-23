"""
Services for the Payments app.
"""

from .stripe_service import StripeService
from .credit_service import CreditService
from .transaction_service import TransactionService
from .payment_method_service import PaymentMethodService

# Composite service for AI token charging
class PaymentService:
    """
    Combined payment service for AI token charging and management.
    
    This service simplifies the token charging process for AI requests
    by combining the credit and transaction services.
    """
    
    def __init__(self):
        """Initialize with required services"""
        self.credit_service = CreditService()
        self.transaction_service = TransactionService()
    
    def charge_tokens(self, user, amount, description=None):
        """
        Charge the user for AI token usage.
        
        Args:
            user: The Django user to charge
            amount: The amount to charge in dollars
            description: Optional description for the transaction
            
        Returns:
            dict: Result of the operation
        """
        # Credits are stored in the database as the actual dollar amount
        # No need to convert dollar amount to credits

        # Force amount to have 4 decimal precision for tiny amounts (like gpt-4.1-nano at $0.01)
        amount = float(f"{float(amount):.4f}")
        
        # Use a default description if none provided
        if not description:
            # Use 4 decimal places for small amounts
            if amount < 0.01:
                description = f"AI token usage: ${amount:.4f}"
            else:
                description = f"AI token usage: ${amount:.2f}"
        
        # Add model info to log for debugging small transactions
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Charging user {user.username} ${amount:.4f} for AI usage")
        
        # First check if user has enough credits
        check_result = self.credit_service.check_credits(user, amount)
        
        if not check_result.get('has_sufficient', False):
            # Return the insufficient credits error
            return {
                'success': False,
                'error': 'Insufficient credits',
                'current_balance': check_result.get('current_balance', 0),
                'required_credits': amount
            }
        
        # Deduct credits - pass the exact dollar amount
        result = self.credit_service.deduct_credits(user, amount, description)
        logger.info(f"Credit deduction result for user {user.username}: {result.get('success', False)}")
        
        return result

__all__ = [
    'StripeService',
    'CreditService',
    'TransactionService',
    'PaymentMethodService',
    'PaymentService'
] 