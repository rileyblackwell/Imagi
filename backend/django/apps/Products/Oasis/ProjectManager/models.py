from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.text import slugify
import os

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
    project_path = models.CharField(
        max_length=500,
        help_text="Absolute path to project directory"
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

    def save(self, *args, **kwargs):
        # Generate slug from name if not set
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Generate project path if not set
        if not self.project_path:
            base_path = os.path.join(
                os.getenv('PROJECTS_ROOT', '/tmp/projects'),
                self.user.username,
                self.slug
            )
            self.project_path = base_path

        super().save(*args, **kwargs)

    def clean(self):
        # Custom validation
        if self.name and len(self.name.strip()) < 3:
            raise ValidationError({
                'name': 'Project name must be at least 3 characters long'
            })
        
        # Ensure project path is unique
        if self.project_path:
            exists = Project.objects.filter(
                project_path=self.project_path
            ).exclude(id=self.id).exists()
            if exists:
                raise ValidationError({
                    'project_path': 'Project path already exists'
                })

    def delete(self, *args, **kwargs):
        """Soft delete by default, with option for hard delete."""
        hard_delete = kwargs.pop('hard_delete', False)
        if hard_delete:
            super().delete(*args, **kwargs)
        else:
            self.is_active = False
            self.save()
