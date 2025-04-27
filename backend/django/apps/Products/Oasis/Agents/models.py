from django.db import models
from django.contrib.auth.models import User
from .services.model_definitions import get_model_choices, get_provider_choices, get_default_provider


class AgentConversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="agent_conversations")
    created_at = models.DateTimeField(auto_now_add=True)
    model_name = models.CharField(max_length=50, choices=get_model_choices())
    provider = models.CharField(max_length=20, choices=get_provider_choices(), default=get_default_provider())
    
    def __str__(self):
        return f"Agent Conversation {self.id} - {self.user.username} using {self.model_name} ({self.provider})"


class SystemPrompt(models.Model):
    conversation = models.OneToOneField(AgentConversation, on_delete=models.CASCADE, related_name="system_prompt")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"System Prompt for Conversation {self.conversation.id}"


class AgentMessage(models.Model):
    conversation = models.ForeignKey(AgentConversation, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=10, choices=[
        ('user', 'User'), 
        ('assistant', 'Assistant'), 
        ('system', 'System')
    ])
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role.capitalize()} message in Conversation {self.conversation.id}"
