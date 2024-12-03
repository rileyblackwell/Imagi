from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('create-checkout-session/', views.create_checkout_session, name='create-checkout-session'),
    path('create-payment-intent/', views.create_payment_intent, name='create-payment-intent'),
    path('success/', views.payment_success, name='payment-success'),
    path('cancel/', views.payment_cancel, name='payment-cancel'),
] 