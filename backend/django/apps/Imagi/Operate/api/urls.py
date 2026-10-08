"""
URL patterns for the Operate app API.
"""

from django.urls import path

from . import views

urlpatterns = [
    # The dashboard: the app half and the business half
    path('projects/<int:project_id>/dashboard/',
         views.DashboardView.as_view(), name='api-operate-dashboard'),
    path('projects/<int:project_id>/app/',
         views.AppMonitorView.as_view(), name='api-operate-app'),
    path('projects/<int:project_id>/app/check/',
         views.UptimeCheckView.as_view(), name='api-operate-app-check'),

    # Public: the live app's page-view tag posts here
    path('beacon/<str:site_key>/',
         views.PageViewBeaconView.as_view(), name='api-operate-beacon'),

    # Financial ledger
    path('projects/<int:project_id>/transactions/',
         views.TransactionListCreateView.as_view(), name='api-operate-transactions'),
    path('projects/<int:project_id>/transactions/<int:pk>/',
         views.TransactionDetailView.as_view(), name='api-operate-transaction-detail'),

    # Invoices
    path('projects/<int:project_id>/invoices/',
         views.InvoiceListCreateView.as_view(), name='api-operate-invoices'),
    path('projects/<int:project_id>/invoices/<int:pk>/',
         views.InvoiceDetailView.as_view(), name='api-operate-invoice-detail'),
    path('projects/<int:project_id>/invoices/<int:pk>/status/',
         views.InvoiceStatusView.as_view(), name='api-operate-invoice-status'),

    # Operational tasks
    path('projects/<int:project_id>/tasks/',
         views.TaskListCreateView.as_view(), name='api-operate-tasks'),
    path('projects/<int:project_id>/tasks/<int:pk>/',
         views.TaskDetailView.as_view(), name='api-operate-task-detail'),
]
