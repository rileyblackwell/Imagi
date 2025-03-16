from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from .models import Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = (
        'username', 
        'email', 
        'first_name', 
        'last_name', 
        'is_staff', 
        'date_joined', 
        'get_credit_balance',
        'view_transactions',
        'view_projects'
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)

    def get_credit_balance(self, obj):
        """Show user's credit balance from the Payments app."""
        try:
            from apps.Payments.models import CreditBalance
            balance = CreditBalance.objects.filter(user=obj).first()
            if balance:
                url = reverse('admin:Payments_creditbalance_change', args=[balance.id])
                return format_html('<a href="{}">{} credits</a>', url, balance.balance)
            else:
                return "0 credits"
        except:
            # Fallback to profile balance if Payments app is not available
            try:
                return f"${obj.profile.balance:.2f}"
            except:
                return "N/A"
    get_credit_balance.short_description = 'Credits'

    def view_transactions(self, obj):
        """Link to user's transaction history."""
        url = reverse('admin:Payments_transaction_changelist') + f'?user__id__exact={obj.id}'
        return format_html('<a href="{}">Transactions</a>', url)
    view_transactions.short_description = 'Transactions'
    
    def view_projects(self, obj):
        """Link to user's projects."""
        try:
            url = reverse('admin:ProjectManager_project_changelist') + f'?user__id__exact={obj.id}'
            return format_html('<a href="{}">Projects</a>', url)
        except:
            return "N/A"
    view_projects.short_description = 'Projects'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Register Profile model directly if needed
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_email', 'balance', 'view_credit_balance', 'view_transactions')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('user',)
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    
    def view_credit_balance(self, obj):
        """Show user's credit balance from the Payments app."""
        try:
            from apps.Payments.models import CreditBalance
            balance = CreditBalance.objects.filter(user=obj.user).first()
            if balance:
                url = reverse('admin:Payments_creditbalance_change', args=[balance.id])
                return format_html('<a href="{}">{} credits</a>', url, balance.balance)
            else:
                return "0 credits"
        except:
            return "N/A"
    view_credit_balance.short_description = 'Credits'
    
    def view_transactions(self, obj):
        """Link to user's transaction history."""
        url = reverse('admin:Payments_transaction_changelist') + f'?user__id__exact={obj.user.id}'
        return format_html('<a href="{}">Transactions</a>', url)
    view_transactions.short_description = 'Transactions'
