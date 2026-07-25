from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'user_link',
        'user_email',
        'generation_status',
        'created_at',
        'last_generated_at',
        'is_active',
        'user_transactions',
        'user_plan'
    )
    list_filter = (
        'is_active',
        'generation_status',
        'created_at',
        'last_generated_at',
        'user'
    )
    search_fields = (
        'name',
        'slug',
        'user__username',
        'user__email',
        'description'
    )
    readonly_fields = (
        'created_at',
        'updated_at',
        'last_generated_at',
        'project_path'
    )
    ordering = ('-updated_at',)
    date_hierarchy = 'created_at'
    
    # Default filtering to only show active projects
    def get_queryset(self, request):
        """Optimize admin list query and filter by default to active projects."""
        qs = super().get_queryset(request).select_related('user')
        # Only show active projects by default
        if not request.GET.get('is_active__exact'):
            qs = qs.filter(is_active=True)
        return qs
    
    fieldsets = (
        ('Project Information', {
            'fields': ('name', 'slug', 'description', 'user')
        }),
        ('Status', {
            'fields': ('is_active', 'generation_status')
        }),
        ('Generated Content', {
            'fields': ('project_path',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_generated_at'),
            'classes': ('collapse',)
        })
    )

    def user_link(self, obj):
        """Display clickable link to user admin."""
        url = reverse('admin:auth_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__username'

    def user_email(self, obj):
        """Display user email."""
        return obj.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'

    def user_transactions(self, obj):
        """Link to user's transaction history."""
        url = reverse('admin:Payments_transaction_changelist') + f'?user__id__exact={obj.user.id}'
        return format_html('<a href="{}">Transactions</a>', url)
    user_transactions.short_description = 'Transactions'

    def user_plan(self, obj):
        """Link to the owner's subscription plan."""
        try:
            from apps.Payments.models import Subscription
            from apps.Payments.services.plans import get_plan

            subscription = Subscription.objects.filter(user=obj.user).first()
            if not subscription:
                return get_plan(None)['name']
            url = reverse('admin:Payments_subscription_change', args=[subscription.id])
            return format_html('<a href="{}">{}</a>', url, get_plan(subscription.plan)['name'])
        except Exception:
            return "N/A"
    user_plan.short_description = 'Plan'

    def has_delete_permission(self, request, obj=None):
        """Only allow hard deletion through admin interface."""
        return request.user.is_superuser

    actions = ['hard_delete_selected']

    def hard_delete_selected(self, request, queryset):
        """Action to permanently delete selected projects."""
        for project in queryset:
            project.delete(hard_delete=True)
    hard_delete_selected.short_description = "Permanently delete selected projects"
