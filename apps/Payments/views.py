from django.shortcuts import render, redirect
from django.conf import settings
import stripe
from .models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_checkout_session(request):
    if request.method == 'POST':
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'T-shirt',
                        },
                        'unit_amount': 2000,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/success/'),
                cancel_url=request.build_absolute_uri('/cancel/'),
            )
            return redirect(checkout_session.url, code=303)
        except Exception as e:
            return str(e)
    return render(request, 'payments/checkout.html')
