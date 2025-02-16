from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'user_link',
        'generation_status',
        'created_at',
        'last_generated_at',
        'is_active'
    )
    list_filter = (
        'is_active',
        'generation_status',
        'created_at',
        'last_generated_at'
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

    def get_queryset(self, request):
        """Optimize admin list query."""
        return super().get_queryset(request).select_related('user')

    def has_delete_permission(self, request, obj=None):
        """Only allow hard deletion through admin interface."""
        return request.user.is_superuser

    actions = ['hard_delete_selected']

    def hard_delete_selected(self, request, queryset):
        """Action to permanently delete selected projects."""
        for project in queryset:
            project.delete(hard_delete=True)
    hard_delete_selected.short_description = "Permanently delete selected projects"
