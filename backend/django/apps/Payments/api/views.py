"""
API views for the Payments app.

Imagi has one plan, Free, with a metered weekly dollar allowance; nothing is
sold. This surface reports usage against that allowance. The paid plans, and
the Stripe Checkout, plan-switch, Billing Portal and subscription webhook
endpoints that sold them, were removed; they come back together if paid plans
do. The history endpoints remain read-only views of past credit purchases.
"""

import stripe
import logging
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..services.stripe_service import StripeService
from ..services.transaction_service import TransactionService
from ..services.payment_method_service import PaymentMethodService
from ..services.plans import list_plans
from ..services.usage_service import get_usage_status
from .serializers import (
    TransactionSerializer,
    PaymentHistorySerializer,
)

logger = logging.getLogger(__name__)

# Initialize services
stripe_service = StripeService()
transaction_service = TransactionService()
payment_method_service = PaymentMethodService()


class UsageStatusView(APIView):
    """Get the user's plan, rolling usage windows, and the plan registry."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            payload = get_usage_status(request.user)
            # The registry too (just Free today), so the frontend can show it.
            payload['plans'] = list_plans()
            return Response(payload)
        except Exception:
            logger.exception("Error fetching usage status")
            raise


class PaymentHistoryView(generics.ListAPIView):
    """List the user's historical credit purchases."""
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
    """List the user's transaction history with optional filtering."""
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

        except Exception:
            logger.exception("Error fetching payment methods")
            raise


def _ensure_stripe_customer(user):
    """The user's Stripe customer id, creating the customer on first need."""
    customer_id = payment_method_service.get_stripe_customer_id(user)
    if customer_id:
        return customer_id
    customer = stripe_service.create_customer(
        email=user.email,
        name=f"{user.first_name} {user.last_name}".strip() or user.username,
        metadata={'user_id': str(user.id)}
    )
    payment_method_service.set_stripe_customer_id(user, customer.id)
    return customer.id


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

        # Save customer ID against the user
        payment_method_service.set_stripe_customer_id(request.user, customer.id)

        return Response({
            'customer_id': customer.id
        })

    except Exception:
        logger.exception("Error setting up customer")
        raise


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

        customer_id = _ensure_stripe_customer(request.user)

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
    except Exception:
        logger.exception("Error attaching payment method")
        raise
