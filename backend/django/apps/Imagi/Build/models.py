"""
Models for the Build app.

Contains the builder workspace models (ProjectLayout, ProjectFile) and the
agent models (AgentConversation, SystemPrompt, AgentMessage), merged from
the former Builder and Agents sub-apps.

Every model pins `db_table` to the table name it had under its original
app label ('Builder' / 'Agents'), so merging the apps required no schema
changes on existing databases.
"""

from django.db import models
from django.contrib.auth import get_user_model
from .services.models_service import (
    get_model_choices,
    get_provider_choices,
    get_default_provider,
)
import logging

logger = logging.getLogger(__name__)

# A single unified agent handles all conversations now. 'chat' remains a
# valid stored value for conversations created before the modes were merged.
MODE_CHOICES = (
    ('chat', 'Chat'),
    ('agent', 'Agent'),
)

# Conversation roles in the lead-thread workspace: one persistent 'lead'
# thread per project, 'task' conversations dispatched from it (each running
# in its own git worktree), and 'chat' for legacy standalone conversations
# (every row predating the split defaults to it and renders as history).
KIND_CHOICES = (
    ('chat', 'Chat'),
    ('lead', 'Lead'),
    ('task', 'Task'),
)

# Kinds whose agent runs edit the shared canonical project tree. Task runs
# edit only their own worktree, so they sit outside the canonical busy guard.
CANONICAL_TREE_KINDS = ('chat', 'lead')

# Review lifecycle for kind='task' conversations ('' for everything else):
# active (running/being worked) -> ready (final reply persisted, awaiting
# review) -> accepted (merged into the canonical tree) or dismissed.
REVIEW_STATUS_CHOICES = (
    ('', 'None'),
    ('active', 'Active'),
    ('ready', 'Ready'),
    ('accepted', 'Accepted'),
    ('dismissed', 'Dismissed'),
)


# ---------------------------------------------------------------------------
# Builder workspace models (formerly the Builder sub-app)
# ---------------------------------------------------------------------------

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

    The working copy on disk (under PROJECTS_ROOT) is the source of truth —
    dev and production both run projects from disk. These rows are a mirror
    of the disk copy, kept so project files are browsable from the Build
    module for debugging, and usable as a backup to rehydrate a working
    copy that has gone missing. Every file mutation — agent tools, builder
    API endpoints, app scaffolding — touches disk first and then writes
    through to this mirror via services.project_files_service.
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
    kind = models.CharField(max_length=10, choices=KIND_CHOICES, default='chat')
    # Lead thread a task was dispatched from. SET_NULL: deleting the lead
    # must not cascade away task history.
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children'
    )
    review_status = models.CharField(
        max_length=10, choices=REVIEW_STATUS_CHOICES, blank=True, default=''
    )
    # Absolute path of the task's git worktree ('<project_path>--wt-<id>'),
    # set when the first task run creates it; cleared on accept/dismiss.
    worktree_path = models.CharField(max_length=500, blank=True, default='')
    # Groups best-of-N sibling tasks spawned from one prompt.
    variant_group = models.CharField(max_length=64, blank=True, default='')
    archived_at = models.DateTimeField(null=True, blank=True)
    # Set when an agent run starts, cleared when it ends. Readers must treat
    # old timestamps as "not running" (staleness guard) because a crashed
    # worker never gets to clear this.
    run_started_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'Agents_agentconversation'
        ordering = ['-updated_at']
        constraints = [
            # Single-lead invariant, enforced at the database so concurrent
            # creates (multi-worker gunicorn, two tabs) cannot slip a second
            # live lead past the API's check-then-create.
            models.UniqueConstraint(
                fields=['user', 'project_id'],
                condition=models.Q(kind='lead', archived_at__isnull=True),
                name='one_live_lead_per_project',
            ),
        ]

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
    # Structured run metadata persisted with assistant replies:
    # {tool_calls?, files_changed?, plan?, usage?} — see
    # services.base_agent.build_message_metadata. NULL for plain replies.
    metadata = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'Agents_agentmessage'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role.capitalize()} message in Conversation {self.conversation.id}"
