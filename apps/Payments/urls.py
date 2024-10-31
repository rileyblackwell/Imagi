from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/', views.create_checkout_session, name='create-checkout-session'),
    path('create-payment-intent/', views.create_payment_intent, name='create-payment-intent'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
] 