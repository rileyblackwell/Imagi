"""
Data migration to update project_path values from oasis_projects to imagi_projects.
"""

from django.db import migrations


def update_project_paths(apps, schema_editor):
    Project = apps.get_model('ProjectManager', 'Project')
    for project in Project.objects.filter(project_path__contains='oasis_projects'):
        project.project_path = project.project_path.replace('oasis_projects', 'imagi_projects')
        project.save(update_fields=['project_path'])


def revert_project_paths(apps, schema_editor):
    Project = apps.get_model('ProjectManager', 'Project')
    for project in Project.objects.filter(project_path__contains='imagi_projects'):
        project.project_path = project.project_path.replace('imagi_projects', 'oasis_projects')
        project.save(update_fields=['project_path'])


class Migration(migrations.Migration):

    dependencies = [
        ('ProjectManager', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(update_project_paths, revert_project_paths),
    ]
