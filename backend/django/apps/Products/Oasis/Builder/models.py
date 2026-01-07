# builder/models.py

from django.db import models
from django.contrib.auth import get_user_model
from .services.models_service import MODELS
import logging

logger = logging.getLogger(__name__)

# Get model IDs and names from centralized model definitions
_model_choices = [(model_id, model_data['name']) for model_id, model_data in MODELS.items()]

class Conversation(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="conversations")
    project_id = models.IntegerField(null=True)  # Store reference to ProjectManager's Project ID
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id} for {self.user.username} - Project ID: {self.project_id or 'None'}"
    
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


class Page(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="pages")
    filename = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['conversation', 'filename']

    def __str__(self):
        return f"Page {self.filename} in Conversation {self.conversation.id}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="messages", null=True)
    role = models.CharField(max_length=10, choices=[('user', 'User'), ('assistant', 'Assistant'), ('system', 'System')])
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role.capitalize()} message for {self.page.filename if self.page else 'unknown page'}"


class AIModel(models.TextChoices):
    # Dynamically create choices from the centralized model definitions
    __choices__ = _model_choices


class ProjectLayout(models.Model):
    """Store custom layout positions and connections for apps in a project"""
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="project_layouts")
    project_id = models.CharField(max_length=255)  # Project ID from ProjectManager
    layout_data = models.JSONField(default=dict)  # Stores positions and connections
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'project_id']
        indexes = [
            models.Index(fields=['user', 'project_id']),
        ]

    def __str__(self):
        return f"Layout for Project {self.project_id} - User {self.user.username}"
