from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .models import (
    Payment,
    StripeCustomer,
    Subscription,
    Transaction,
    UsageEvent,
    CreditPackage,
    PaymentMethod,
)
from .services.plans import get_plan
from .services.usage_service import get_usage_status


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_email', 'plan', 'get_allowance', 'get_weekly_usage', 'updated_at')
    list_filter = ('plan', 'updated_at')
    search_fields = ('user__username', 'user__email', 'stripe_subscription_id')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-updated_at',)

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'

    def get_allowance(self, obj):
        return f"${get_plan(obj.plan)['weekly_usd']:.2f}/week"
    get_allowance.short_description = 'Allowance'

    def get_weekly_usage(self, obj):
        weekly = get_usage_status(obj.user)['windows']['weekly']
        return f"${weekly['used_usd']:.2f} of ${weekly['limit_usd']:.2f}"
    get_weekly_usage.short_description = 'This week'


@admin.register(UsageEvent)
class UsageEventAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'model_name', 'get_cost_display', 'total_tokens', 'conversation_id')
    list_filter = ('model_name', 'created_at')
    search_fields = ('user__username', 'user__email')
    # Append-only metering: editing a row would falsify a user's allowance.
    readonly_fields = ('user', 'created_at', 'model_name', 'input_tokens',
                       'output_tokens', 'total_tokens', 'cost_usd', 'conversation_id')
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_cost_display(self, obj):
        return f"${obj.cost_usd:.4f}"
    get_cost_display.short_description = 'Metered cost'


@admin.register(StripeCustomer)
class StripeCustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_email', 'stripe_customer_id', 'last_updated', 'view_transactions')
    list_filter = ('last_updated',)
    search_fields = ('user__username', 'user__email', 'stripe_customer_id')
    readonly_fields = ('last_updated',)
    ordering = ('-last_updated',)

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'

    def view_transactions(self, obj):
        url = reverse('admin:Payments_transaction_changelist') + f'?user__id__exact={obj.user.id}'
        return format_html('<a href="{}">View Transactions</a>', url)
    view_transactions.short_description = 'Transactions'


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
            return format_html('<span style="color: green; font-weight: bold">+${}</span>', obj.amount)
        elif obj.transaction_type in ['usage', 'refund']:
            return format_html('<span style="color: red; font-weight: bold">${}</span>', obj.amount)
        return f"${obj.amount}"
    get_amount_display.short_description = 'Amount'


@admin.register(CreditPackage)
class CreditPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'credits', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    ordering = ('id',)


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
        return f"•••• {obj.last4}"
    get_card_info.short_description = 'Card'

    def get_default_status(self, obj):
        return obj.is_default
    get_default_status.short_description = 'Default'
    get_default_status.boolean = True
