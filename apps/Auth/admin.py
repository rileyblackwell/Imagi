from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_credits', 'get_projects', 'view_payments')

    def get_credits(self, obj):
        return obj.profile.credits
    get_credits.short_description = 'API Credits'

    def get_projects(self, obj):
        return ", ".join([project.name for project in obj.projects.all()])
    get_projects.short_description = 'Projects'

    def view_payments(self, obj):
        return f'<a href="/admin/Payments/payment/?user__id={obj.id}">View Payments</a>'
    view_payments.short_description = 'Payment History'
    view_payments.allow_tags = True  # Allow HTML in the admin display

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
