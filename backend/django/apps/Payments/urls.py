from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'payments'

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'packages', views.CreditPackageViewSet, basename='package')
router.register(r'models', views.AIModelViewSet, basename='ai-model')
router.register(r'usage/history', views.AIModelUsageViewSet, basename='usage-history')

urlpatterns = [
    # ViewSet routes
    path('', include(router.urls)),
    
    # API Views
    path('create-payment-intent/', views.PaymentIntentView.as_view(), name='create-payment-intent'),
    path('verify/', views.VerifyPaymentView.as_view(), name='verify-payment'),
    path('usage/check/', views.CheckUsageAvailabilityView.as_view(), name='check-usage-availability'),
    path('balance/', views.get_balance, name='get-balance'),
    
    # Template Views (if needed)
    path('success/', views.payment_success, name='payment-success'),
    path('cancel/', views.payment_cancel, name='payment-cancel'),
] 