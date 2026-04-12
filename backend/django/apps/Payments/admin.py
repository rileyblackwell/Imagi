from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .models import Payment, CreditBalance, Transaction, CreditPlan, CreditPackage, PaymentMethod

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_email', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email', 'stripe_payment_id')
    readonly_fields = ('stripe_payment_id', 'created_at', 'updated_at')
    ordering = ('-created_at',)

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'

    def get_amount_display(self, obj):
        return f"${obj.amount:.2f}"
    get_amount_display.short_description = 'Amount'

@admin.register(CreditBalance)
class CreditBalanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_email', 'get_balance_display', 'last_updated', 'view_transactions')
    list_filter = ('last_updated',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('last_updated',)
    ordering = ('-last_updated',)
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    
    def get_balance_display(self, obj):
        return f"{obj.balance} credits"
    get_balance_display.short_description = 'Balance'
    
    def view_transactions(self, obj):
        url = reverse('admin:Payments_transaction_changelist') + f'?user__id__exact={obj.user.id}'
        return format_html('<a href="{}">View Transactions</a>', url)
    view_transactions.short_description = 'Transactions'

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_email', 'transaction_type', 'get_amount_display', 'status', 'created_at', 'description')
    list_filter = ('transaction_type', 'status', 'created_at', 'user')
    search_fields = ('user__username', 'user__email', 'description', 'stripe_payment_intent_id')
    readonly_fields = ('stripe_payment_intent_id', 'stripe_checkout_session_id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    
    def get_amount_display(self, obj):
        # Format the amount based on transaction type
        if obj.transaction_type in ['purchase', 'bonus']:
            return format_html('<span style="color: green; font-weight: bold">+{} credits</span>', obj.amount)
        elif obj.transaction_type in ['usage', 'refund']:
            return format_html('<span style="color: red; font-weight: bold">{} credits</span>', obj.amount)
        return f"{obj.amount} credits"
    get_amount_display.short_description = 'Amount'

@admin.register(CreditPlan)
class CreditPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'credits', 'get_price_display', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'stripe_price_id')
    ordering = ('price_cents',)
    
    def get_price_display(self, obj):
        return f"${obj.price_cents/100:.2f}"
    get_price_display.short_description = 'Price'

@admin.register(CreditPackage)
class CreditPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'credits', 'get_price_display', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    ordering = ('id',)
    
    def get_price_display(self, obj):
        # Assuming the price field might be named differently
        if hasattr(obj, 'price'):
            return f"${obj.price:.2f}"
        elif hasattr(obj, 'price_cents'):
            return f"${obj.price_cents/100:.2f}"
        return "N/A"
    get_price_display.short_description = 'Price'

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_email', 'get_card_info', 'get_default_status', 'created_at')
    list_filter = ('is_default', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    
    def get_card_info(self, obj):
        # Handle different field names for card information
        last_four = getattr(obj, 'last_four', getattr(obj, 'last4', 'XXXX'))
        return f"•••• {last_four}"
    get_card_info.short_description = 'Card'
    
    def get_default_status(self, obj):
        return obj.is_default
    get_default_status.short_description = 'Default'
    get_default_status.boolean = True
