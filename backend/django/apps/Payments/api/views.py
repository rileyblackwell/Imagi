"""
API views for the Payments app.
"""

import stripe
from decimal import Decimal
import logging
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db import transaction

from ..models import CreditBalance, Transaction, CreditPlan
from .serializers import (
    TransactionSerializer,
    CreditPlanSerializer,
)

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

class CreditBalanceView(APIView):
    """Get user's credit balance."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            balance = CreditBalance.objects.get_or_create(user=request.user)[0]
            return Response({
                'balance': float(balance.balance)
            })
        except Exception as e:
            logger.error(f"Error fetching balance: {str(e)}")
            return Response(
                {'error': 'Failed to fetch balance'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CreditPlanListView(generics.ListAPIView):
    """List all active credit plans."""
    serializer_class = CreditPlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CreditPlan.objects.filter(is_active=True)

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

        # Convert amount to cents for Stripe
        amount_cents = int(amount * 100)
        
        # Calculate credits (1:1 ratio - $1 = 1 credit)
        credits = amount

        # Create PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency='usd',
            metadata={
                'user_id': str(request.user.id),
                'credits': str(credits)
            },
            automatic_payment_methods={
                'enabled': True,
            }
        )
        
        # Create pending transaction
        Transaction.objects.create(
            user=request.user,
            amount=credits,  # Store the credit amount
            transaction_type='purchase',
            status='pending',
            stripe_payment_intent_id=intent.id,
            description=f'Purchase of {credits} credits'
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
def confirm_payment(request):
    """Confirm a successful payment and add credits to user's balance."""
    try:
        payment_intent_id = request.data.get('payment_intent_id')
        if not payment_intent_id:
            return Response({
                'error': 'Payment intent ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the transaction
        transaction = get_object_or_404(
            Transaction,
            stripe_payment_intent_id=payment_intent_id,
            user=request.user
        )
        
        if transaction.status == 'completed':
            return Response({
                'message': 'Payment already processed',
                'balance': float(request.user.credit_balance.balance)
            })
        
        # Verify payment with Stripe
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        if payment_intent.status != 'succeeded':
            return Response({
                'error': 'Payment not successful'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update credit balance and transaction status
        with transaction.atomic():
            balance = CreditBalance.objects.get_or_create(user=request.user)[0]
            balance.balance = Decimal(str(float(balance.balance) + transaction.amount))
            balance.save()
            
            transaction.status = 'completed'
            transaction.save()
        
        return Response({
            'message': 'Payment processed successfully',
            'credits_added': float(transaction.amount),
            'new_balance': float(balance.balance)
        })
        
    except Exception as e:
        logger.error(f"Error confirming payment: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_credits(request):
    """Check if user has sufficient credits for an operation."""
    try:
        required_credits = float(request.data.get('required_credits', 0))
        if required_credits <= 0:
            return Response({
                'error': 'Invalid credit amount'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        balance = CreditBalance.objects.get_or_create(user=request.user)[0]
        has_sufficient_credits = float(balance.balance) >= required_credits
        
        if not has_sufficient_credits:
            # Get the smallest plan that covers the required credits
            plan = CreditPlan.objects.filter(
                credits__gte=required_credits,
                is_active=True
            ).order_by('credits').first()
            
            return Response({
                'has_sufficient_credits': False,
                'current_balance': float(balance.balance),
                'required_credits': required_credits,
                'suggested_plan': CreditPlanSerializer(plan).data if plan else None
            })
        
        return Response({
            'has_sufficient_credits': True,
            'current_balance': float(balance.balance)
        })
        
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
        if credits_to_deduct <= 0:
            return Response({
                'error': 'Invalid credit amount'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            balance = CreditBalance.objects.select_for_update().get(user=request.user)
            
            if float(balance.balance) < credits_to_deduct:
                return Response({
                    'error': 'Insufficient credits'
                }, status=status.HTTP_402_PAYMENT_REQUIRED)
            
            # Create usage transaction
            Transaction.objects.create(
                user=request.user,
                amount=-credits_to_deduct,
                transaction_type='usage',
                status='completed'
            )
            
            # Update balance
            balance.balance = Decimal(str(float(balance.balance) - credits_to_deduct))
            balance.save()
        
        return Response({
            'message': 'Credits deducted successfully',
            'new_balance': float(balance.balance)
        })
        
    except CreditBalance.DoesNotExist:
        return Response({
            'error': 'No credit balance found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error deducting credits: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TransactionHistoryView(generics.ListAPIView):
    """List user's transaction history."""
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(
            user=self.request.user
        ).order_by('-created_at')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def webhook(request):
    """Handle Stripe webhooks."""
    try:
        event = stripe.Webhook.construct_event(
            request.body,
            request.META['HTTP_STRIPE_SIGNATURE'],
            settings.STRIPE_WEBHOOK_SECRET
        )
        
        if event.type == 'payment_intent.succeeded':
            payment_intent = event.data.object
            transaction = Transaction.objects.get(
                stripe_payment_intent_id=payment_intent.id,
                status='pending'
            )
            
            with transaction.atomic():
                # Update transaction status
                transaction.status = 'completed'
                transaction.save()
                
                # Add credits to user's balance
                balance = CreditBalance.objects.get_or_create(
                    user=transaction.user
                )[0]
                balance.balance = Decimal(str(float(balance.balance) + transaction.amount))
                balance.save()
                
            logger.info(f"Credits added via webhook: {transaction.amount} for user {transaction.user.id}")
            
        return Response({'status': 'success'})
        
    except stripe.error.SignatureVerificationError:
        return Response(
            {'error': 'Invalid signature'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 