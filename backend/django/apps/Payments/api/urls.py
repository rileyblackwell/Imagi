"""
URL patterns for the Payments app API.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Core payment functionality
    path('balance/', views.CreditBalanceView.as_view(), name='api-credit-balance'),
    path('process/', views.process_payment, name='api-process-payment'),
    
    # Credit management
    path('check-credits/', views.check_credits, name='api-check-credits'),
    path('deduct-credits/', views.deduct_credits, name='api-deduct-credits'),
    
    # Credit packages & history
    path('packages/', views.CreditPackagesView.as_view(), name='api-credit-packages'),
    path('history/', views.PaymentHistoryView.as_view(), name='api-payment-history'),
    path('transactions/', views.TransactionHistoryView.as_view(), name='api-transaction-history'),
    
    # Payment method management
    path('payment-methods/', views.PaymentMethodsView.as_view(), name='api-payment-methods'),
    path('attach-payment-method/', views.attach_payment_method, name='api-attach-payment-method'),
    path('setup-customer/', views.setup_customer, name='api-setup-customer'),
    
    # Stripe webhook (essential for payment events)
    path('webhook/', views.webhook, name='api-stripe-webhook'),
] 