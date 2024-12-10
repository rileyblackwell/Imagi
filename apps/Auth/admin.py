from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile

# Define inline admin for Profile
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'

# Extend the existing UserAdmin
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_credits', 'is_staff')
    
    def get_credits(self, obj):
        return obj.profile.credits if hasattr(obj, 'profile') else 0
    get_credits.short_description = 'Credits'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Register Profile model directly if needed
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'credits')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('user',)
