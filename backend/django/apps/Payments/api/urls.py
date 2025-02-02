"""
URL patterns for the Payments app API.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Credit balance endpoint
    path('balance/', views.CreditBalanceView.as_view(), name='api-credit-balance'),
    
    # Payment processing endpoints
    path('create-payment-intent/', views.create_payment_intent, name='api-create-payment-intent'),
    path('confirm-payment/', views.confirm_payment, name='api-confirm-payment'),
    
    # Stripe webhook
    path('webhook/', views.webhook, name='api-stripe-webhook'),
    
    # Transaction history
    path('transactions/', views.TransactionHistoryView.as_view(), name='api-transaction-history'),
] 