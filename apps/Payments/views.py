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

@require_http_methods(["POST"])
@login_required
def create_payment_intent(request):
    try:
        data = json.loads(request.body)
        amount = float(data.get('amount', 10.00))
        
        # Validate amount
        if amount < 10 or amount > 100:
            return JsonResponse({'error': 'Amount must be between $10.00 and $100.00'}, status=400)

        # Convert amount to cents for Stripe
        amount_cents = int(amount * 100)

        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency='usd',
            metadata={
                'user_id': str(request.user.id),
                'amount': str(amount),
            },
            automatic_payment_methods={
                'enabled': True,
            }
        )
        
        try:
            # Create pending payment record
            Payment.objects.create(
                user=request.user,
                amount=amount,
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
    except ValueError:
        return JsonResponse({'error': 'Invalid amount format'}, status=400)
    except Exception as e:
        logger.error(f"Payment intent creation failed: {str(e)}")
        return JsonResponse({'error': str(e)}, status=403)

@login_required
def payment_success(request):
    payment_intent_id = request.GET.get('payment_intent')
    if not payment_intent_id:
        logger.warning("Payment success called without payment_intent")
        return redirect('landing_page')
        
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        if intent.status == 'succeeded':
            # Update payment record
            payment = Payment.objects.get(stripe_payment_id=payment_intent_id)
            payment.status = 'completed'
            payment.save()
            
            # Update user profile balance
            user_profile = request.user.profile
            user_profile.balance += payment.amount
            user_profile.save()
            
            return render(request, 'payments/success.html', {
                'amount_added': payment.amount,
                'new_balance': user_profile.balance
            })
    except Exception as e:
        logger.error(f"Payment success processing failed: {str(e)}")
        messages.error(request, str(e))
        return redirect('landing_page')

@login_required
def payment_cancel(request):
    return render(request, 'payments/cancel.html')

@login_required
def get_balance(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Force refresh from database
        request.user.profile.refresh_from_db()
        return JsonResponse({
            'balance': float(request.user.profile.balance)
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)
