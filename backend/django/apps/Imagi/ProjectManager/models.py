from django.db import models
from django.conf import settings as django_settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.text import slugify
import os
import logging

User = get_user_model()

class Project(models.Model):
    """
    Project model representing a user's application project.
    Handles the metadata and filesystem organization for generated projects.
    """
    name = models.CharField(
        max_length=255,
        help_text="Name of the project"
    )
    slug = models.SlugField(
        max_length=255,
        blank=True,
        help_text="URL-friendly version of the name"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional project description"
    )
    design_preferences = models.TextField(
        blank=True,
        default="",
        help_text="Optional founder-provided design/style direction for the initial AI build"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='managed_projects',
        help_text="Project owner"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(
        default=True,
        help_text="Soft deletion status"
    )
    project_dir = models.CharField(
        max_length=500,
        blank=True,
        help_text=(
            "Project directory, relative to settings.PROJECTS_ROOT. Stored "
            "relative so a project created in one checkout still resolves in "
            "another; read it through the project_path property, which joins "
            "it to the configured root. A path outside that root (a temp "
            "directory in tests, a legacy row) is stored absolute and returned "
            "unchanged."
        )
    )
    last_generated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time project files were generated"
    )
    generation_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('generating', 'Generating'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='pending',
        help_text="Current status of project generation"
    )
    is_initialized = models.BooleanField(default=False)

    class Meta:
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'name'],
                condition=models.Q(is_active=True),
                name='unique_active_project_name_per_user'
            )
        ]
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['slug']),
            models.Index(fields=['generation_status'])
        ]

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    @property
    def project_path(self):
        """Absolute path to the project directory on this machine.

        Everything outside this model works in absolute paths; only storage is
        relative. Returns '' for a project whose directory has not been
        assigned yet, matching the old CharField's empty default.
        """
        if not self.project_dir:
            return ''
        if os.path.isabs(self.project_dir):
            return self.project_dir
        return os.path.join(django_settings.PROJECTS_ROOT, self.project_dir)

    @project_path.setter
    def project_path(self, value):
        """Store an absolute path, relative to PROJECTS_ROOT where possible.

        Django's Model.__init__ routes property kwargs through here, so
        `Project(project_path=...)` and `objects.create(project_path=...)` keep
        working. Paths outside the root — pytest temp directories, a project
        pinned somewhere by PROJECTS_ROOT env override — cannot be expressed
        relative to it and are kept absolute.
        """
        if not value:
            self.project_dir = ''
            return
        root = os.path.abspath(django_settings.PROJECTS_ROOT)
        candidate = os.path.abspath(value)
        if candidate == root or candidate.startswith(root + os.sep):
            self.project_dir = os.path.relpath(candidate, root)
        else:
            self.project_dir = value

    def save(self, *args, **kwargs):
        # Generate slug from name if not set
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            
            # Ensure the slug is unique
            while Project.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
                
            self.slug = slug
        
        # Generate project directory if not set. Built relative directly —
        # a new project always belongs under PROJECTS_ROOT.
        if not self.project_dir:
            self.project_dir = os.path.join(self.user.username, self.slug)

        super().save(*args, **kwargs)

    def clean(self):
        # Custom validation
        if self.name and len(self.name.strip()) < 3:
            raise ValidationError({
                'name': 'Project name must be at least 3 characters long'
            })
        
        # Ensure project directory is unique. Compared on the stored relative
        # value, so two checkouts resolving the same project don't read as a
        # collision.
        if self.project_dir:
            exists = Project.objects.filter(
                project_dir=self.project_dir
            ).exclude(id=self.id).exists()
            if exists:
                raise ValidationError({
                    'project_dir': 'Project path already exists'
                })

    def delete(self, *args, **kwargs):
        """Soft delete by default, with option for hard delete."""
        hard_delete = kwargs.pop('hard_delete', False)
        
        if hard_delete:
            # Log the hard delete operation
            logger = logging.getLogger(__name__)
            logger.info(f"Hard deleting project {self.id}: {self.name}")
            
            # Call the parent's delete method for actual database deletion
            return super().delete(*args, **kwargs)
        else:
            # Soft delete - just mark as inactive
            self.is_active = False
            self.save(update_fields=['is_active', 'updated_at'])
