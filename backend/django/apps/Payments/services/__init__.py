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
        # Convert dollar amount to credits (1 credit = $0.01)
        credit_amount = amount * 100
        
        # Use a default description if none provided
        if not description:
            description = f"AI token usage: ${amount:.4f}"
        
        # First check if user has enough credits
        check_result = self.credit_service.check_credits(user, credit_amount)
        
        if not check_result.get('has_sufficient', False):
            # Handle insufficient credits
            # In a real system, you might want to prevent the request or add credits automatically
            pass
        
        # Deduct credits
        return self.credit_service.deduct_credits(user, credit_amount, description)

__all__ = [
    'StripeService',
    'CreditService',
    'TransactionService',
    'PaymentMethodService',
    'PaymentService'
] 