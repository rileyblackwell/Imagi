"""
URL patterns for the Payments app API.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Plan usage against the metered allowance
    path('usage/', views.UsageStatusView.as_view(), name='api-usage-status'),

    # History of past credit purchases (read-only; nothing writes these now)
    path('history/', views.PaymentHistoryView.as_view(), name='api-payment-history'),
    path('transactions/', views.TransactionHistoryView.as_view(), name='api-transaction-history'),

    # Payment method management
    path('payment-methods/', views.PaymentMethodsView.as_view(), name='api-payment-methods'),
    path('attach-payment-method/', views.attach_payment_method, name='api-attach-payment-method'),
    path('setup-customer/', views.setup_customer, name='api-setup-customer'),

    # Subscription checkout & management
    path('create-checkout-session/', views.create_checkout_session, name='api-create-checkout-session'),
    path('session-status/', views.get_session_status, name='api-session-status'),
    path('create-portal-session/', views.create_portal_session, name='api-create-portal-session'),

    # Stripe webhook (the only path that grants or revokes a plan)
    path('webhook/', views.webhook, name='api-stripe-webhook'),
]
