"""
Models for the Build app.

Contains the builder workspace models (Conversation, Page, Message,
ProjectLayout) and the agent models (AgentConversation, SystemPrompt,
AgentMessage), merged from the former Builder and Agents sub-apps.

Every model pins `db_table` to the table name it had under its original
app label ('Builder' / 'Agents'), so merging the apps required no schema
changes on existing databases.
"""

from django.db import models
from django.contrib.auth import get_user_model
from .services.models_service import (
    MODELS,
    get_model_choices,
    get_provider_choices,
    get_default_provider,
)
import logging

logger = logging.getLogger(__name__)

# Get model IDs and names from centralized model definitions
_model_choices = [(model_id, model_data['name']) for model_id, model_data in MODELS.items()]

# A single unified agent handles all conversations now. 'chat' remains a
# valid stored value for conversations created before the modes were merged.
MODE_CHOICES = (
    ('chat', 'Chat'),
    ('agent', 'Agent'),
)


# ---------------------------------------------------------------------------
# Builder workspace models (formerly the Builder sub-app)
# ---------------------------------------------------------------------------

class Conversation(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="conversations")
    project_id = models.IntegerField(null=True)  # Store reference to ProjectManager's Project ID
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Builder_conversation'

    def __str__(self):
        return f"Conversation {self.id} for {self.user.username} - Project ID: {self.project_id or 'None'}"

    @property
    def project_name(self):
        """Get the project name from the ProjectManager app"""
        if not self.project_id:
            return None

        try:
            from apps.Imagi.ProjectManager.models import Project
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
        db_table = 'Builder_page'
        unique_together = ['conversation', 'filename']

    def __str__(self):
        return f"Page {self.filename} in Conversation {self.conversation.id}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="messages", null=True)
    role = models.CharField(max_length=10, choices=[('user', 'User'), ('assistant', 'Assistant'), ('system', 'System')])
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Builder_message'

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
        db_table = 'Builder_projectlayout'
        unique_together = ['user', 'project_id']
        indexes = [
            models.Index(fields=['user', 'project_id']),
        ]

    def __str__(self):
        return f"Layout for Project {self.project_id} - User {self.user.username}"


class ProjectFile(models.Model):
    """Database copy of a single file in a user's project.

    The database is the durable store for project files: production serves
    and edits files from these rows, while development additionally keeps a
    local working copy on disk (under PROJECTS_ROOT) that mirrors them.
    Every file mutation — agent tools, builder API endpoints, app
    scaffolding — writes through to both places via
    services.project_files_service.
    """
    project = models.ForeignKey(
        'ProjectManager.Project',
        on_delete=models.CASCADE,
        related_name='files',
    )
    path = models.CharField(max_length=500)  # project-relative, POSIX separators
    content = models.TextField(blank=True, default='')
    file_type = models.CharField(max_length=20, blank=True, default='')
    size = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Build_projectfile'
        unique_together = ['project', 'path']
        indexes = [
            models.Index(fields=['project', 'path']),
        ]

    def __str__(self):
        return f"{self.path} (project {self.project_id})"


# ---------------------------------------------------------------------------
# Agent models (formerly the Agents sub-app)
# ---------------------------------------------------------------------------

class AgentConversation(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="agent_conversations")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    model_name = models.CharField(max_length=50, choices=get_model_choices())
    provider = models.CharField(max_length=20, choices=get_provider_choices(), default=get_default_provider())
    project_id = models.IntegerField(null=True, blank=True)  # Store reference to ProjectManager's Project ID
    title = models.CharField(max_length=120, blank=True, default='')
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default='agent')
    archived_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'Agents_agentconversation'
        ordering = ['-updated_at']

    def __str__(self):
        return f"Agent Conversation {self.id} - {self.user.username} using {self.model_name} ({self.provider})"

    @property
    def project_name(self):
        """Get the project name from the ProjectManager app"""
        if not self.project_id:
            return None

        try:
            from apps.Imagi.ProjectManager.models import Project
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

    class Meta:
        db_table = 'Agents_systemprompt'

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
        db_table = 'Agents_agentmessage'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role.capitalize()} message in Conversation {self.conversation.id}"
