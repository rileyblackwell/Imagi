from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import JsonResponse
import stripe
import json
from .models import Payment
from django.contrib import messages

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def create_checkout_session(request):
    return render(request, 'payments/checkout.html', {
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY
    })

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
                'user_id': request.user.id,
                'credits': credit_amount,
            },
            automatic_payment_methods={
                'enabled': True,
            }
        )
        
        # Create pending payment record
        Payment.objects.create(
            user=request.user,
            amount=credit_amount,
            credits=credit_amount,
            stripe_payment_id=intent.id,
            status='pending'
        )
        
        return JsonResponse({
            'clientSecret': intent.client_secret
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=403)

@login_required
def payment_success(request):
    payment_intent_id = request.GET.get('payment_intent')
    if payment_intent_id:
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
            messages.error(request, str(e))
    
    return redirect('dashboard')

@login_required
def payment_cancel(request):
    return render(request, 'payments/cancel.html')
