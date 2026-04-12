"""
API views for the Payments app.
"""

import stripe
import logging
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings

from ..services.stripe_service import StripeService
from ..services.credit_service import CreditService
from ..services.transaction_service import TransactionService
from ..services.payment_method_service import PaymentMethodService
from .serializers import (
    TransactionSerializer,
    CreditPackageSerializer,
    PaymentHistorySerializer,
)

logger = logging.getLogger(__name__)

# Initialize services
stripe_service = StripeService()
credit_service = CreditService()
transaction_service = TransactionService()
payment_method_service = PaymentMethodService()

class CreditBalanceView(APIView):
    """Get user's credit balance."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            balance = credit_service.get_balance(request.user)
            return Response({
                'balance': balance
            })
        except Exception as e:
            logger.error(f"Error fetching balance: {str(e)}")
            return Response(
                {'error': 'Failed to fetch balance'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CreditPackagesView(APIView):
    """Get available credit packages."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            packages = transaction_service.get_credit_packages()
            serializer = CreditPackageSerializer(packages, many=True)
            return Response({
                'packages': serializer.data
            })
        except Exception as e:
            logger.error(f"Error fetching packages: {str(e)}")
            return Response(
                {'error': 'Failed to fetch packages'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PaymentHistoryView(generics.ListAPIView):
    """List user's payment history."""
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentHistorySerializer

    def get_queryset(self):
        return transaction_service.get_payment_history(self.request.user)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'payments': serializer.data
        })

class TransactionHistoryView(generics.ListAPIView):
    """List user's transaction history with optional filtering."""
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        status_filter = self.request.query_params.get('status')
        sort_by = self.request.query_params.get('sort_by', 'created_at')
        sort_order = self.request.query_params.get('sort_order', 'desc')
        
        result = transaction_service.get_transactions(
            self.request.user,
            status=status_filter,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return result['transactions']
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'transactions': serializer.data,
            'total_count': queryset.count()
        })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment_intent(request):
    """Create a Stripe PaymentIntent for credit purchase."""
    try:
        amount = request.data.get('amount')
        if not amount:
            return Response({
                'error': 'Amount is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate amount
        amount = float(amount)
        if amount < 5 or amount > 1000:
            return Response({
                'error': 'Amount must be between $5 and $1,000'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create a payment intent
        metadata = {
            'user_id': str(request.user.id),
            'credits': str(amount)
        }
        
        # Use direct payment instead
        payment_method_id = request.data.get('payment_method_id')
        if not payment_method_id:
            return Response({
                'error': 'Payment method ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        intent = stripe_service.create_direct_payment(amount, payment_method_id, metadata)
        
        # Create a transaction record
        transaction_service.create_purchase_transaction(
            request.user, 
            amount, 
            stripe_payment_intent_id=intent.id
        )
        
        return Response({
            'clientSecret': intent.client_secret
        })
        
    except ValueError:
        return Response({
            'error': 'Invalid amount format'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error creating payment intent: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_payment(request):
    """Process payment and add credits to user's account."""
    try:
        amount = request.data.get('amount')
        payment_method_id = request.data.get('paymentMethodId')
        
        if not amount or not payment_method_id:
            return Response({
                'error': 'Amount and payment method ID are required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        amount = float(amount)
        
        # Create payment intent with immediate confirmation
        metadata = {
            'user_id': str(request.user.id),
            'credits': str(amount)
        }
        
        intent = stripe_service.create_direct_payment(amount, payment_method_id, metadata)
        
        # Create transaction record
        transaction = transaction_service.create_purchase_transaction(
            request.user,
            amount,
            stripe_payment_intent_id=intent.id
        )
        
        # If payment intent succeeded immediately, update balance
        if intent.status == 'succeeded':
            result = credit_service.add_credits(request.user, amount, transaction)
            
            return Response({
                'success': True,
                'message': 'Payment processed successfully',
                'new_balance': result['new_balance'],
                'credits_added': amount
            })
        
        # If payment needs additional actions
        return Response({
            'requires_action': True,
            'payment_intent_client_secret': intent.client_secret
        })
        
    except stripe.error.CardError as e:
        return Response({
            'error': e.user_message
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error processing payment: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_payment(request):
    """Confirm a successful payment and add credits to user's balance."""
    try:
        payment_intent_id = request.data.get('payment_intent_id')
        if not payment_intent_id:
            return Response({
                'error': 'Payment intent ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the transaction
        transaction = transaction_service.get_transaction_by_payment_intent(
            request.user, payment_intent_id
        )
        
        if not transaction:
            return Response({
                'error': 'Transaction not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if transaction.status == 'completed':
            return Response({
                'message': 'Payment already processed',
                'balance': credit_service.get_balance(request.user)
            })
        
        # Verify payment with Stripe
        payment_intent = stripe_service.get_payment_intent(payment_intent_id)
        if payment_intent.status != 'succeeded':
            return Response({
                'error': 'Payment not successful'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Add credits to user's balance
        result = credit_service.add_credits(request.user, float(transaction.amount), transaction)
        
        return Response({
            'message': 'Payment processed successfully',
            'credits_added': float(transaction.amount),
            'new_balance': result['new_balance']
        })
        
    except Exception as e:
        logger.error(f"Error confirming payment: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_payment(request):
    """Verify a payment was successful."""
    try:
        payment_intent_id = request.data.get('payment_intent_id')
        if not payment_intent_id:
            return Response({
                'error': 'Payment intent ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Verify payment with Stripe
        payment_intent = stripe_service.get_payment_intent(payment_intent_id)
        
        # Get the transaction if it exists
        transaction = transaction_service.get_transaction_by_payment_intent(
            request.user, payment_intent_id
        )
        
        if not transaction:
            return Response({
                'error': 'Transaction not found'
            }, status=status.HTTP_404_NOT_FOUND)
            
        # If payment succeeded but transaction not updated
        if payment_intent.status == 'succeeded' and transaction.status != 'completed':
            result = credit_service.add_credits(request.user, float(transaction.amount), transaction)
            
            return Response({
                'success': True,
                'status': 'completed',
                'credits_added': float(transaction.amount),
                'new_balance': result['new_balance']
            })
            
        return Response({
            'success': True,
            'status': transaction.status,
            'payment_intent_status': payment_intent.status
        })
        
    except stripe.error.StripeError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error verifying payment: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_credits(request):
    """Check if user has sufficient credits for an operation."""
    try:
        required_credits = float(request.data.get('required_credits', 0))
        
        result = credit_service.check_credits(request.user, required_credits)
        
        if not result['success']:
            return Response({
                'error': result['error']
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(result)
        
    except Exception as e:
        logger.error(f"Error checking credits: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deduct_credits(request):
    """Deduct credits from user's balance for service usage."""
    try:
        credits_to_deduct = float(request.data.get('credits', 0))
        
        result = credit_service.deduct_credits(
            request.user, 
            credits_to_deduct, 
            transaction_description=request.data.get('description')
        )
        
        if not result['success']:
            if 'No credit balance found' in result.get('error', ''):
                return Response({
                    'error': 'No credit balance found'
                }, status=status.HTTP_404_NOT_FOUND)
            elif 'Insufficient credits' in result.get('error', ''):
                return Response({
                    'error': 'Insufficient credits'
                }, status=status.HTTP_402_PAYMENT_REQUIRED)
            else:
                return Response({
                    'error': result['error']
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'message': 'Credits deducted successfully',
            'new_balance': result['new_balance']
        })
        
    except Exception as e:
        logger.error(f"Error deducting credits: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PaymentMethodsView(APIView):
    """Get user's saved payment methods."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Get customer ID
            customer_id = payment_method_service.get_stripe_customer_id(request.user)
            
            if not customer_id:
                return Response([])
                
            # Get payment methods from Stripe
            payment_methods = stripe_service.list_payment_methods(customer_id)
            
            return Response(payment_methods)
                
        except Exception as e:
            logger.error(f"Error fetching payment methods: {str(e)}")
            return Response(
                {'error': 'Failed to fetch payment methods'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def setup_customer(request):
    """Set up a Stripe customer for the user."""
    try:
        # Check if user already has a Stripe customer ID
        customer_id = payment_method_service.get_stripe_customer_id(request.user)
        
        if customer_id:
            try:
                # Verify customer exists
                customer = stripe_service.get_customer(customer_id)
                return Response({
                    'customer_id': customer.id
                })
            except stripe.error.InvalidRequestError:
                # Customer doesn't exist in Stripe, create new one
                pass
                
        # Create a new customer
        customer = stripe_service.create_customer(
            email=request.user.email,
            name=f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            metadata={
                'user_id': str(request.user.id)
            }
        )
        
        # Save customer ID to user profile
        payment_method_service.set_stripe_customer_id(request.user, customer.id)
        
        return Response({
            'customer_id': customer.id
        })
        
    except Exception as e:
        logger.error(f"Error setting up customer: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def attach_payment_method(request):
    """Attach a payment method to the user's Stripe customer."""
    try:
        payment_method_id = request.data.get('payment_method_id')
        if not payment_method_id:
            return Response({
                'error': 'Payment method ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Ensure user has a Stripe customer
        customer_id = payment_method_service.get_stripe_customer_id(request.user)
        
        if not customer_id:
            # Create a customer first
            customer = stripe_service.create_customer(
                email=request.user.email,
                name=f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                metadata={
                    'user_id': str(request.user.id)
                }
            )
            customer_id = customer.id
            payment_method_service.set_stripe_customer_id(request.user, customer_id)
            
        # Attach payment method to customer
        payment_method = stripe_service.attach_payment_method(payment_method_id, customer_id)
        
        # Store payment method details
        card = payment_method.card
        payment_method_service.create_payment_method(request.user, {
            'payment_method_id': payment_method.id,
            'card_brand': card.brand,
            'last4': card.last4,
            'exp_month': card.exp_month,
            'exp_year': card.exp_year
        })
        
        return Response({
            'success': True,
            'payment_method': payment_method
        })
        
    except stripe.error.StripeError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error attaching payment method: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    """Create a Stripe Checkout Session for purchasing credits."""
    try:
        amount = request.data.get('amount')
        plan_id = request.data.get('plan_id')
        success_url = request.data.get('success_url', f"{settings.FRONTEND_URL}/payments/success")
        cancel_url = request.data.get('cancel_url', f"{settings.FRONTEND_URL}/payments/cancel")
        
        if not amount and not plan_id:
            return Response({
                'error': 'Either amount or plan_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Prepare line items and metadata
        if plan_id:
            plan = transaction_service.get_plan_by_id(plan_id)
            if not plan:
                return Response({
                    'error': 'Plan not found'
                }, status=status.HTTP_404_NOT_FOUND)
                
            price_id = plan.stripe_price_id
            credits = plan.credits
        else:
            # Convert to float and validate
            amount = float(amount)
            if amount < 5 or amount > 1000:
                return Response({
                    'error': 'Amount must be between $5 and $1,000'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            # For one-time purchases without a plan, create the price on-the-fly
            credits = amount  # 1:1 ratio
            price = stripe_service.create_price(
                unit_amount=int(amount * 100),
                metadata={
                    'credits': str(credits)
                }
            )
            price_id = price.id
            
        # Create checkout session
        metadata = {
            'user_id': str(request.user.id),
            'credits': str(credits)
        }
        
        line_items = [
            {
                'price': price_id,
                'quantity': 1,
            }
        ]
        
        checkout_session = stripe_service.create_checkout_session(
            line_items=line_items,
            metadata=metadata,
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        return Response({
            'session_id': checkout_session.id,
            'checkout_url': checkout_session.url
        })
        
    except ValueError:
        return Response({
            'error': 'Invalid amount format'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_session_status(request):
    """Get the status of a Stripe Checkout Session."""
    try:
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response({
                'error': 'Session ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Retrieve session from Stripe
        session = stripe_service.get_session_status(session_id)
        
        # Check if payment succeeded
        if session.payment_status == 'paid':
            # Find or create the transaction
            transaction = transaction_service.get_transaction_by_checkout_session(session_id)
            
            if not transaction:
                # Create transaction record
                credits = float(session.metadata.get('credits', 0))
                transaction = transaction_service.create_purchase_transaction(
                    request.user,
                    credits,
                    stripe_checkout_session_id=session_id,
                    description=f'Purchase of {credits} credits via Checkout'
                )
                
                # Add credits to user's balance
                credit_service.add_credits(request.user, credits, transaction)
            
            return Response({
                'status': 'complete',
                'payment_status': session.payment_status,
                'credits_added': float(transaction.amount)
            })
            
        return Response({
            'status': 'pending',
            'payment_status': session.payment_status
        })
        
    except stripe.error.StripeError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error checking session status: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PlansView(generics.ListAPIView):
    """List available subscription plans."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Retrieve plans from Stripe
            plans = stripe_service.list_plans()
            
            # Format for response
            formatted_plans = []
            for plan in plans:
                formatted_plans.append({
                    'id': plan.id,
                    'name': plan.nickname or 'Subscription',
                    'price': plan.unit_amount / 100,
                    'currency': plan.currency,
                    'interval': plan.recurring.interval,
                    'credits': float(plan.metadata.get('credits', 0)) if plan.metadata else 0
                })
                
            return Response(formatted_plans)
            
        except Exception as e:
            logger.error(f"Error fetching plans: {str(e)}")
            return Response(
                {'error': 'Failed to fetch plans'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_webhook(request):
    """Verify a webhook event from Stripe."""
    try:
        event_id = request.data.get('event_id')
        if not event_id:
            return Response({
                'error': 'Event ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Retrieve event from Stripe
        event = stripe.Event.retrieve(event_id)
        
        return Response({
            'verified': True,
            'event_type': event.type
        })
        
    except stripe.error.StripeError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error verifying webhook: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def webhook(request):
    """Handle Stripe webhooks."""
    try:
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        try:
            event = stripe_service.verify_webhook_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            logger.error("Invalid webhook payload")
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid webhook signature")
            return Response(status=status.HTTP_400_BAD_REQUEST)
            
        # Handle specific event types
        if event.type == 'payment_intent.succeeded':
            payment_intent = event.data.object
            handle_payment_intent_succeeded(payment_intent)
            
        elif event.type == 'checkout.session.completed':
            session = event.data.object
            handle_checkout_session_completed(session)
            
        # Return success response
        return Response({'status': 'success'})
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def handle_payment_intent_succeeded(payment_intent):
    """Handle a successful payment intent."""
    try:
        # Find the transaction
        transaction = transaction_service.get_transaction_by_payment_intent(None, payment_intent.id)
        
        if not transaction:
            logger.warning(f"Transaction not found for payment intent {payment_intent.id}")
            return
        
        # Add credits to user's balance
        credit_service.add_credits(transaction.user, float(transaction.amount), transaction)
        
        logger.info(f"Credits added via webhook: {transaction.amount} for user {transaction.user.id}")
        
    except Exception as e:
        logger.error(f"Error handling payment intent succeeded: {str(e)}")

def handle_checkout_session_completed(session):
    """Handle a completed checkout session."""
    try:
        # Skip if not paid
        if session.payment_status != 'paid':
            return
            
        # Extract user ID and credits from metadata
        user_id = session.metadata.get('user_id')
        credits = float(session.metadata.get('credits', 0))
        
        if not user_id or credits <= 0:
            logger.warning(f"Invalid metadata in checkout session {session.id}")
            return
            
        # Check if transaction already exists
        transaction = transaction_service.get_transaction_by_checkout_session(session.id)
        
        if transaction:
            logger.info(f"Transaction already exists for session {session.id}")
            return
            
        # Get user model
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get user
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.error(f"User {user_id} not found for checkout session {session.id}")
            return
            
        # Create transaction and add credits
        transaction = transaction_service.create_purchase_transaction(
            user,
            credits,
            stripe_checkout_session_id=session.id,
            description=f'Purchase of {credits} credits via Checkout'
        )
        
        credit_service.add_credits(user, credits, transaction)
        
        logger.info(f"Credits added via checkout: {credits} for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error handling checkout session completed: {str(e)}") 