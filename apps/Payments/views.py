from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import JsonResponse
import stripe
import json
from .models import Payment
from django.contrib import messages
import logging
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

@ensure_csrf_cookie
@login_required
def create_checkout_session(request):
    return render(request, 'payments/checkout.html', {
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY
    })

@require_http_methods(["POST"])
@login_required
def create_payment_intent(request):
    try:
        data = json.loads(request.body)
        credit_amount = int(data.get('credit_amount', 10))
        
        # Validate credit amount
        if credit_amount not in [10, 15, 20]:
            return JsonResponse({'error': 'Invalid credit amount'}, status=400)

        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=credit_amount * 100,  # Convert to cents
            currency='usd',
            metadata={
                'user_id': str(request.user.id),  # Convert to string
                'credits': str(credit_amount),    # Convert to string
            },
            automatic_payment_methods={
                'enabled': True,
            }
        )
        
        try:
            # Create pending payment record
            Payment.objects.create(
                user=request.user,
                amount=credit_amount,
                credits=credit_amount,
                stripe_payment_id=intent.id,
                status='pending'
            )
        except Exception as e:
            logger.error(f"Failed to create payment record: {str(e)}")
            # If payment record creation fails, cancel the payment intent
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
def payment_success(request):
    payment_intent_id = request.GET.get('payment_intent')
    if not payment_intent_id:
        logger.warning("Payment success called without payment_intent")
        return redirect('dashboard')
        
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        if intent.status == 'succeeded':
            # Update payment record
            payment = Payment.objects.get(stripe_payment_id=payment_intent_id)
            payment.status = 'completed'
            payment.save()
            
            # Update user credits
            request.user.credits = request.user.credits + payment.credits
            request.user.save()
            
            return render(request, 'payments/success.html', {
                'credits_added': payment.credits,
                'new_balance': request.user.credits
            })
    except Exception as e:
        logger.error(f"Payment success processing failed: {str(e)}")
        messages.error(request, str(e))
        return redirect('dashboard')

@login_required
def payment_cancel(request):
    return render(request, 'payments/cancel.html')
