from django.contrib import admin
from .models import AgentConversation, SystemPrompt, AgentMessage


@admin.register(AgentConversation)
class AgentConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'model_name', 'created_at')
    list_filter = ('model_name', 'created_at')
    search_fields = ('user__username', 'model_name')


@admin.register(SystemPrompt)
class SystemPromptAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'created_at', 'updated_at')
    search_fields = ('content',)


@admin.register(AgentMessage)
class AgentMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'role', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('content',)
