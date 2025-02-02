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
    CreditBalanceSerializer,
    TransactionSerializer,
    CreditPlanSerializer,
    UserCreditBalanceSerializer
)

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

class CreditBalanceView(generics.RetrieveAPIView):
    """Get user's credit balance."""
    serializer_class = CreditBalanceSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(CreditBalance, user=self.request.user)

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
        plan_id = request.data.get('plan_id')
        if not plan_id:
            return Response({
                'error': 'Missing plan_id'
            }, status=status.HTTP_400_BAD_REQUEST)

        credit_plan = get_object_or_404(CreditPlan, id=plan_id, is_active=True)
        
        # Create PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=credit_plan.price_cents,
            currency='usd',
            metadata={
                'user_id': request.user.id,
                'credits': credit_plan.credits,
                'plan_id': credit_plan.id
            }
        )
        
        # Create pending transaction
        Transaction.objects.create(
            user=request.user,
            amount=credit_plan.credits,
            transaction_type='purchase',
            status='pending',
            stripe_payment_intent_id=intent.id
        )
        
        return Response({
            'client_secret': intent.client_secret,
            'amount': credit_plan.price_cents,
            'credits': credit_plan.credits
        })
        
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
                'error': 'Missing payment_intent_id'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the transaction
        transaction = get_object_or_404(
            Transaction,
            stripe_payment_intent_id=payment_intent_id,
            user=request.user
        )
        
        if transaction.status == 'completed':
            return Response({
                'message': 'Payment already processed'
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