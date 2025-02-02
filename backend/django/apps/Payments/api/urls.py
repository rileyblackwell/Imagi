"""
URL patterns for the Payments app API.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Credit balance endpoints
    path('balance/', views.CreditBalanceView.as_view(), name='api-credit-balance'),
    path('plans/', views.CreditPlanListView.as_view(), name='api-credit-plans'),
    
    # Payment processing endpoints
    path('create-payment-intent/', views.create_payment_intent, name='api-create-payment-intent'),
    path('confirm-payment/', views.confirm_payment, name='api-confirm-payment'),
    
    # Credit management endpoints
    path('check-credits/', views.check_credits, name='api-check-credits'),
    path('deduct-credits/', views.deduct_credits, name='api-deduct-credits'),
    
    # Transaction history
    path('transactions/', views.TransactionHistoryView.as_view(), name='api-transaction-history'),
] 