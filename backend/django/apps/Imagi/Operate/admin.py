from django.contrib import admin

from .models import AppMonitor, Invoice, OperationsTask, PageView, Transaction, UptimeCheck


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


@admin.register(AppMonitor)
class AppMonitorAdmin(admin.ModelAdmin):
    list_display = ('project', 'live_url', 'updated_at')
    search_fields = ('project__name', 'live_url')
    readonly_fields = ('site_key', 'created_at', 'updated_at')


@admin.register(UptimeCheck)
class UptimeCheckAdmin(admin.ModelAdmin):
    list_display = ('url', 'project', 'is_up', 'status_code', 'response_ms', 'checked_at')
    list_filter = ('is_up',)
    search_fields = ('url', 'project__name')


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ('path', 'project', 'referrer_host', 'created_at')
    search_fields = ('path', 'project__name')
