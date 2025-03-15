"""
URL patterns for the Payments app API.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Credit balance endpoint
    path('balance/', views.CreditBalanceView.as_view(), name='api-credit-balance'),
    
    # Payment processing endpoints
    path('create-intent/', views.create_payment_intent, name='api-create-payment-intent'),
    path('process/', views.process_payment, name='api-process-payment'),
    path('confirm-payment/', views.confirm_payment, name='api-confirm-payment'),
    path('verify/', views.verify_payment, name='api-verify-payment'),
    
    # Credit packages
    path('packages/', views.CreditPackagesView.as_view(), name='api-credit-packages'),
    
    # Transaction history
    path('history/', views.PaymentHistoryView.as_view(), name='api-payment-history'),
    path('transactions/', views.TransactionHistoryView.as_view(), name='api-transaction-history'),
    
    # Credit management
    path('check-credits/', views.check_credits, name='api-check-credits'),
    path('deduct-credits/', views.deduct_credits, name='api-deduct-credits'),
    
    # Payment methods
    path('payment-methods/', views.PaymentMethodsView.as_view(), name='api-payment-methods'),
    path('attach-payment-method/', views.attach_payment_method, name='api-attach-payment-method'),
    path('setup-customer/', views.setup_customer, name='api-setup-customer'),
    
    # Checkout session
    path('create-checkout-session/', views.create_checkout_session, name='api-create-checkout-session'),
    path('session-status/', views.get_session_status, name='api-session-status'),
    
    # Plans
    path('plans/', views.PlansView.as_view(), name='api-plans'),
    
    # Stripe webhook
    path('webhook/', views.webhook, name='api-stripe-webhook'),
    path('verify-webhook/', views.verify_webhook, name='api-verify-webhook'),
] 