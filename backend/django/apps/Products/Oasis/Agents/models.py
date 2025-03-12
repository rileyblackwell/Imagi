from django.db import models
from django.contrib.auth.models import User


class AgentConversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="agent_conversations")
    created_at = models.DateTimeField(auto_now_add=True)
    model_name = models.CharField(max_length=50, choices=[
        ('gpt-4o', 'GPT-4o'),
        ('gpt-4o-mini', 'GPT-4o Mini'),
        ('claude-3-5-sonnet-20241022', 'Claude 3.5 Sonnet'),
    ])
    provider = models.CharField(max_length=20, choices=[
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
    ], default='anthropic')
    
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
