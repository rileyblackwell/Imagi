# builder/models.py

from django.db import models
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conversations")
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
