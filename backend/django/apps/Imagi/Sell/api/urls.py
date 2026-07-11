"""
URL patterns for the Sell app API.
"""

from django.urls import path

from . import views

urlpatterns = [
    # Stripe configuration
    path('projects/<int:project_id>/settings/',
         views.SellSettingsView.as_view(), name='api-sell-settings'),
    path('projects/<int:project_id>/settings/verify/',
         views.VerifyConnectionView.as_view(), name='api-sell-verify'),

    # Dashboard
    path('projects/<int:project_id>/overview/',
         views.OverviewView.as_view(), name='api-sell-overview'),

    # Catalog
    path('projects/<int:project_id>/products/',
         views.ProductListCreateView.as_view(), name='api-sell-products'),
    path('projects/<int:project_id>/products/<int:pk>/',
         views.ProductDetailView.as_view(), name='api-sell-product-detail'),
    path('projects/<int:project_id>/products/<int:pk>/payment-link/',
         views.ProductPaymentLinkView.as_view(), name='api-sell-product-payment-link'),

    # Orders
    path('projects/<int:project_id>/orders/',
         views.OrderListView.as_view(), name='api-sell-orders'),
    path('projects/<int:project_id>/orders/<int:pk>/',
         views.OrderDetailView.as_view(), name='api-sell-order-detail'),
    path('projects/<int:project_id>/orders/<int:pk>/fulfill/',
         views.OrderFulfillView.as_view(), name='api-sell-order-fulfill'),
    path('projects/<int:project_id>/orders/<int:pk>/sync/',
         views.OrderSyncView.as_view(), name='api-sell-order-sync'),

    # Customers (CRM)
    path('projects/<int:project_id>/customers/',
         views.CustomerListCreateView.as_view(), name='api-sell-customers'),
    path('projects/<int:project_id>/customers/<int:pk>/',
         views.CustomerDetailView.as_view(), name='api-sell-customer-detail'),

    # Storefront (public, called by the business's app or its customers)
    path('storefront/<int:project_id>/products/',
         views.PublicProductListView.as_view(), name='api-sell-storefront-products'),
    path('storefront/<int:project_id>/checkout/',
         views.PublicCheckoutView.as_view(), name='api-sell-storefront-checkout'),
    path('storefront/<int:project_id>/sessions/<str:session_id>/',
         views.PublicSessionStatusView.as_view(), name='api-sell-storefront-session'),

    # Stripe callbacks (signature-authenticated, no user session)
    path('webhooks/<int:project_id>/stripe/',
         views.StripeWebhookView.as_view(), name='api-sell-webhook-stripe'),
]
