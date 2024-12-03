from django.contrib import admin
from .models import UserProject

@admin.register(UserProject)
class UserProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    search_fields = ('name', 'user__username')
    list_filter = ('created_at',)
