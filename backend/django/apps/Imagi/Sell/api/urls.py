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

    # Stripe Connect
    path('projects/<int:project_id>/connect/start/',
         views.ConnectStartView.as_view(), name='api-sell-connect-start'),
    path('projects/<int:project_id>/connect/refresh/',
         views.ConnectRefreshView.as_view(), name='api-sell-connect-refresh'),
    path('projects/<int:project_id>/connect/disconnect/',
         views.ConnectDisconnectView.as_view(), name='api-sell-connect-disconnect'),
    path('projects/<int:project_id>/server-key/',
         views.ServerKeyView.as_view(), name='api-sell-server-key'),

    # Dashboard
    path('projects/<int:project_id>/overview/',
         views.OverviewView.as_view(), name='api-sell-overview'),

    # Prebuilt payment pages (dropped into the user's generated project)
    path('projects/<int:project_id>/app-payments/',
         views.AppPaymentsView.as_view(), name='api-sell-app-payments'),
    path('projects/<int:project_id>/app-payments/install/',
         views.AppPaymentsInstallView.as_view(), name='api-sell-app-payments-install'),

    # Subscriptions
    path('projects/<int:project_id>/subscriptions/',
         views.SubscriptionListView.as_view(), name='api-sell-subscriptions'),

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

    # Server API (the business's own backend, server-key authenticated)
    path('storefront/<int:project_id>/usage/',
         views.UsageReportView.as_view(), name='api-sell-storefront-usage'),
    path('storefront/<int:project_id>/subscriptions/',
         views.CustomerPlansView.as_view(), name='api-sell-storefront-subscriptions'),

    # Stripe callbacks (signature-authenticated, no user session)
    path('webhooks/connect/',
         views.ConnectWebhookView.as_view(), name='api-sell-webhook-connect'),
    path('webhooks/<int:project_id>/stripe/',
         views.StripeWebhookView.as_view(), name='api-sell-webhook-stripe'),
]
