from django.contrib import admin

from .models import Customer, Order, OrderItem, Product, SellSettings


@admin.register(SellSettings)
class SellSettingsAdmin(admin.ModelAdmin):
    list_display = ('project', 'currency', 'account_name', 'last_verified_at')
    search_fields = ('project__name', 'account_name', 'account_email')
    readonly_fields = (
        'stripe_secret_key_encrypted', 'stripe_webhook_secret_encrypted',
        'created_at', 'updated_at',
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'price_cents', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description', 'project__name')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'email', 'project', 'source', 'created_at')
    list_filter = ('source',)
    search_fields = ('name', 'email', 'phone', 'project__name')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'status', 'amount_total_cents', 'customer_email', 'created_at')
    list_filter = ('status',)
    search_fields = (
        'customer_email', 'customer_name', 'project__name',
        'stripe_checkout_session_id', 'stripe_payment_intent_id',
    )
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderItemInline]
