"""
Data migration to update project_path values after imagi_projects moved from
apps/Imagi/imagi_projects to apps/Imagi/Build/imagi_projects.

Note: this only rewrites the stored paths. The physical directory must be
moved to the new location as part of deploying this change (mirroring how
0002 handled the oasis_projects -> imagi_projects rename).
"""

from django.db import migrations

OLD_SEGMENT = 'apps/Imagi/imagi_projects'
NEW_SEGMENT = 'apps/Imagi/Build/imagi_projects'


def update_project_paths(apps, schema_editor):
    Project = apps.get_model('ProjectManager', 'Project')
    for project in Project.objects.filter(project_path__contains=OLD_SEGMENT):
        project.project_path = project.project_path.replace(OLD_SEGMENT, NEW_SEGMENT)
        project.save(update_fields=['project_path'])


def revert_project_paths(apps, schema_editor):
    Project = apps.get_model('ProjectManager', 'Project')
    for project in Project.objects.filter(project_path__contains=NEW_SEGMENT):
        project.project_path = project.project_path.replace(NEW_SEGMENT, OLD_SEGMENT)
        project.save(update_fields=['project_path'])


class Migration(migrations.Migration):

    dependencies = [
        ('ProjectManager', '0002_rename_oasis_to_imagi_projects'),
    ]

    operations = [
        migrations.RunPython(update_project_paths, revert_project_paths),
    ]
