"""
URL patterns for the Operate app API.
"""

from django.urls import path

from . import views

urlpatterns = [
    # Central hub dashboard
    path('projects/<int:project_id>/dashboard/',
         views.DashboardView.as_view(), name='api-operate-dashboard'),

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
