from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import JsonResponse
import stripe
import json
from .models import Payment, CreditPackage, AIModel, AIModelUsage
from django.contrib import messages
import logging
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.db.models import Sum
from decimal import Decimal
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import (
    CreditPackageSerializer, PaymentSerializer, AIModelSerializer,
    AIModelUsageSerializer, CreatePaymentIntentSerializer,
    VerifyPaymentSerializer, CheckUsageAvailabilitySerializer
)

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

CREDITS_PER_DOLLAR = 10  # $1 = 10 credits ($10 = 100 credits)

@ensure_csrf_cookie
@login_required
def create_checkout_session(request):
    # Force refresh user profile from database
    request.user.profile.refresh_from_db()
    
    context = {
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'current_balance': request.user.profile.balance
    }
    logger.info(f"Stripe Key (first 10 chars): {settings.STRIPE_PUBLISHABLE_KEY[:10]}...")
    logger.info(f"Current user balance: ${request.user.profile.balance}")
    return render(request, 'payments/checkout.html', context)

@login_required
@require_http_methods(["GET"])
def get_credit_packages(request):
    """Get all active credit packages"""
    try:
        packages = CreditPackage.objects.filter(is_active=True).values(
            'id', 'name', 'amount', 'credits', 'features', 'is_popular'
        )
        return JsonResponse(list(packages), safe=False)
    except Exception as e:
        logger.error(f"Error fetching credit packages: {str(e)}")
        return JsonResponse({'error': 'Failed to fetch credit packages'}, status=500)

@login_required
@require_http_methods(["GET"])
def get_credit_package(request, package_id):
    """Get a specific credit package"""
    try:
        package = get_object_or_404(CreditPackage, id=package_id, is_active=True)
        return JsonResponse({
            'id': package.id,
            'name': package.name,
            'amount': float(package.amount),
            'credits': package.credits,
            'features': package.features,
            'is_popular': package.is_popular
        })
    except Exception as e:
        logger.error(f"Error fetching credit package {package_id}: {str(e)}")
        return JsonResponse({'error': 'Failed to fetch credit package'}, status=500)

@require_http_methods(["POST"])
@login_required
def create_payment_intent(request):
    """Create a Stripe PaymentIntent for credit purchase"""
    try:
        data = json.loads(request.body)
        package_id = data.get('packageId')
        custom_amount = data.get('amount')
        
        if package_id:
            # Get the credit package
            package = get_object_or_404(CreditPackage, id=package_id, is_active=True)
            amount = float(package.amount)
            credits = float(package.credits)
        elif custom_amount:
            # Handle custom amount
            amount = float(custom_amount)
            if amount < 5 or amount > 1000:
                return JsonResponse({
                    'error': 'Custom amount must be between $5.00 and $1,000.00'
                }, status=400)
            credits = amount  # 1:1 ratio for custom amounts
        else:
            return JsonResponse({
                'error': 'Either packageId or amount is required'
            }, status=400)

        # Convert amount to cents for Stripe
        amount_cents = int(amount * 100)

        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency='usd',
            metadata={
                'user_id': str(request.user.id),
                'package_id': package_id if package_id else 'custom',
                'credits': str(credits),
            },
            automatic_payment_methods={
                'enabled': True,
            }
        )
        
        try:
            # Create pending payment record
            Payment.objects.create(
                user=request.user,
                package_id=package_id if package_id else None,
                amount=Decimal(str(amount)),
                credits=Decimal(str(credits)),
                stripe_payment_id=intent.id,
                status='pending'
            )
        except Exception as e:
            logger.error(f"Failed to create payment record: {str(e)}")
            stripe.PaymentIntent.cancel(intent.id)
            raise
        
        return JsonResponse({
            'clientSecret': intent.client_secret
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Payment intent creation failed: {str(e)}")
        return JsonResponse({'error': str(e)}, status=403)

@login_required
@require_http_methods(["POST"])
def verify_payment(request):
    """Verify a payment and update user credits"""
    try:
        data = json.loads(request.body)
        payment_intent_id = data.get('payment_intent_id')
        
        if not payment_intent_id:
            return JsonResponse({'error': 'Payment intent ID is required'}, status=400)
            
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        with transaction.atomic():
            # Get and update payment record
            payment = get_object_or_404(Payment, stripe_payment_id=payment_intent_id)
            
            if payment.status == 'completed':
                return JsonResponse({'status': 'already_completed'})
            
            if intent.status == 'succeeded':
                # Update payment status
                payment.status = 'completed'
                payment.save()
                
                # Update user credits
                profile = request.user.profile
                profile.credits += payment.credits
                profile.save()
                
                return JsonResponse({
                    'status': 'success',
                    'credits_added': payment.credits,
                    'new_balance': profile.credits
                })
            else:
                payment.status = 'failed'
                payment.save()
                return JsonResponse({'error': 'Payment verification failed'}, status=400)
                
    except Exception as e:
        logger.error(f"Payment verification failed: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def get_ai_models(request):
    """Get all active AI models and their costs"""
    try:
        models = AIModel.objects.filter(is_active=True).values(
            'id', 'name', 'cost_per_use', 'description'
        )
        return JsonResponse(list(models), safe=False)
    except Exception as e:
        logger.error(f"Error fetching AI models: {str(e)}")
        return JsonResponse({'error': 'Failed to fetch AI models'}, status=500)

@login_required
@require_http_methods(["GET"])
def get_usage_history(request):
    """Get user's AI model usage history"""
    try:
        usage = AIModelUsage.objects.filter(user=request.user).select_related('model').order_by('-used_at')[:50]
        usage_data = [{
            'model': usage.model.name,
            'cost': float(usage.cost),
            'used_at': usage.used_at.isoformat(),
            'success': usage.success
        } for usage in usage]
        return JsonResponse(usage_data, safe=False)
    except Exception as e:
        logger.error(f"Error fetching usage history: {str(e)}")
        return JsonResponse({'error': 'Failed to fetch usage history'}, status=500)

@login_required
@require_http_methods(["POST"])
def check_usage_availability(request):
    """Check if user has enough credits to use a specific AI model"""
    try:
        data = json.loads(request.body)
        model_id = data.get('model_id')
        
        if not model_id:
            return JsonResponse({'error': 'model_id is required'}, status=400)
            
        model = get_object_or_404(AIModel, id=model_id, is_active=True)
        user_credits = request.user.profile.credits
        
        can_use = user_credits >= model.cost_per_use
        
        return JsonResponse({
            'can_use': can_use,
            'credits_needed': float(model.cost_per_use),
            'current_credits': float(user_credits)
        })
    except Exception as e:
        logger.error(f"Error checking usage availability: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["GET"])
def get_balance(request):
    """Get user's current credit balance and usage summary"""
    try:
        # Force refresh from database
        request.user.profile.refresh_from_db()
        
        # Get total spent on AI models
        total_spent = AIModelUsage.objects.filter(
            user=request.user
        ).aggregate(total=Sum('cost'))['total'] or 0
        
        return JsonResponse({
            'balance': float(request.user.profile.credits),
            'total_spent': float(total_spent),
            'usage_count': AIModelUsage.objects.filter(user=request.user).count()
        })
    except Exception as e:
        logger.error(f"Error fetching balance: {str(e)}")
        return JsonResponse({'error': 'Failed to fetch balance'}, status=500)

@login_required
def payment_success(request):
    """Handle successful payment redirect"""
    payment_intent_id = request.GET.get('payment_intent')
    if not payment_intent_id:
        logger.warning("Payment success called without payment_intent")
        return redirect('home')
        
    try:
        payment = get_object_or_404(Payment, stripe_payment_id=payment_intent_id)
        return render(request, 'payments/success.html', {
            'amount': float(payment.amount),
            'credits': payment.credits,
            'package_name': payment.package.name
        })
    except Exception as e:
        logger.error(f"Payment success page error: {str(e)}")
        return redirect('home')

@login_required
def payment_cancel(request):
    """Handle cancelled payment"""
    return render(request, 'payments/cancel.html')

class CreditPackageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing credit packages.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CreditPackageSerializer
    queryset = CreditPackage.objects.filter(is_active=True)

class AIModelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing AI models.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AIModelSerializer
    queryset = AIModel.objects.filter(is_active=True)

class AIModelUsageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing AI model usage history.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AIModelUsageSerializer

    def get_queryset(self):
        return AIModelUsage.objects.filter(
            user=self.request.user
        ).select_related('model').order_by('-used_at')[:50]

class PaymentIntentView(APIView):
    """
    Create a Stripe PaymentIntent for credit purchase.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreatePaymentIntentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = serializer.validated_data
            package_id = data.get('packageId')
            custom_amount = data.get('amount')

            if package_id:
                package = get_object_or_404(CreditPackage, id=package_id, is_active=True)
                amount = float(package.amount)
                credits = float(package.credits)
            else:
                amount = float(custom_amount)
                credits = amount  # 1:1 ratio for custom amounts

            # Convert amount to cents for Stripe
            amount_cents = int(amount * 100)

            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency='usd',
                metadata={
                    'user_id': str(request.user.id),
                    'package_id': package_id if package_id else 'custom',
                    'credits': str(credits),
                },
                automatic_payment_methods={'enabled': True}
            )

            # Create pending payment record
            Payment.objects.create(
                user=request.user,
                package_id=package_id if package_id else None,
                amount=Decimal(str(amount)),
                credits=Decimal(str(credits)),
                stripe_payment_id=intent.id,
                status='pending'
            )

            return Response({'clientSecret': intent.client_secret})

        except Exception as e:
            logger.error(f"Payment intent creation failed: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class VerifyPaymentView(APIView):
    """
    Verify a payment and update user credits.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = VerifyPaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment_intent_id = serializer.validated_data['payment_intent_id']
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            with transaction.atomic():
                payment = get_object_or_404(Payment, stripe_payment_id=payment_intent_id)

                if payment.status == 'completed':
                    return Response({'status': 'already_completed'})

                if intent.status == 'succeeded':
                    # Update payment status
                    payment.status = 'completed'
                    payment.save()

                    # Update user credits
                    profile = request.user.profile
                    profile.credits += payment.credits
                    profile.save()

                    return Response({
                        'status': 'success',
                        'credits_added': float(payment.credits),
                        'new_balance': float(profile.credits)
                    })
                else:
                    payment.status = 'failed'
                    payment.save()
                    return Response(
                        {'error': 'Payment verification failed'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

        except Exception as e:
            logger.error(f"Payment verification failed: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CheckUsageAvailabilityView(APIView):
    """
    Check if user has enough credits to use a specific AI model.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CheckUsageAvailabilitySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            model = get_object_or_404(
                AIModel,
                id=serializer.validated_data['model_id'],
                is_active=True
            )
            user_credits = request.user.profile.credits
            can_use = user_credits >= model.cost_per_use

            return Response({
                'can_use': can_use,
                'credits_needed': float(model.cost_per_use),
                'current_credits': float(user_credits)
            })

        except Exception as e:
            logger.error(f"Error checking usage availability: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_balance(request):
    """
    Get user's current credit balance and usage summary.
    """
    try:
        request.user.profile.refresh_from_db()
        total_spent = AIModelUsage.objects.filter(
            user=request.user
        ).aggregate(total=Sum('cost'))['total'] or 0

        return Response({
            'balance': float(request.user.profile.credits),
            'total_spent': float(total_spent),
            'usage_count': AIModelUsage.objects.filter(user=request.user).count()
        })
    except Exception as e:
        logger.error(f"Error fetching balance: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
