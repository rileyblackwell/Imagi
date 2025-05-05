from django.db import models
from django.contrib.auth import get_user_model
from apps.Products.Oasis.Builder.services.models_service import get_model_choices, get_provider_choices, get_default_provider
import logging


logger = logging.getLogger(__name__)


class AgentConversation(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="agent_conversations")
    created_at = models.DateTimeField(auto_now_add=True)
    model_name = models.CharField(max_length=50, choices=get_model_choices())
    provider = models.CharField(max_length=20, choices=get_provider_choices(), default=get_default_provider())
    project_id = models.IntegerField(null=True, blank=True)  # Store reference to ProjectManager's Project ID
    
    def __str__(self):
        return f"Agent Conversation {self.id} - {self.user.username} using {self.model_name} ({self.provider})"
    
    @property
    def project_name(self):
        """Get the project name from the ProjectManager app"""
        if not self.project_id:
            return None
            
        try:
            from apps.Products.Oasis.ProjectManager.models import Project
            project = Project.objects.filter(id=self.project_id, user=self.user).first()
            return project.name if project else None
        except Exception as e:
            logger.error(f"Error getting project name: {str(e)}")
            return None


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
