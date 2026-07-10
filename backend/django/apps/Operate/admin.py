from django.contrib import admin

from .models import Invoice, OperationsTask, Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('description', 'project', 'kind', 'category', 'amount', 'occurred_on')
    list_filter = ('kind', 'category')
    search_fields = ('description', 'project__name')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('number', 'project', 'customer_name', 'status', 'total', 'issue_date', 'due_date')
    list_filter = ('status',)
    search_fields = ('number', 'customer_name', 'customer_email', 'project__name')
    readonly_fields = ('total', 'sent_at', 'paid_at', 'created_at', 'updated_at')


@admin.register(OperationsTask)
class OperationsTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'status', 'priority', 'due_date', 'created_at')
    list_filter = ('status', 'priority')
    search_fields = ('title', 'project__name')
