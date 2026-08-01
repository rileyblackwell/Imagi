"""Store project directories relative to PROJECTS_ROOT instead of absolutely.

An absolute path pinned each project to the checkout that created it. In
development every git worktree has its own PROJECTS_ROOT, so a project built in
one worktree kept resolving into that worktree from every other one — and
deleting that worktree stranded the files. Storing the path relative lets one
shared root serve every checkout.

The forward data step deliberately splits on the `imagi_projects/` segment
rather than calling os.path.relpath against the configured root: the stored
paths point at *other* checkouts' roots, so relpath would produce a pile of
`../..` escapes back out of the current one. Anything without that segment (a
temp directory from a test run, a row already written by newer code) is left
absolute, which the model's project_path property returns unchanged.
"""

import os

from django.db import migrations, models

# The directory name every historical PROJECTS_ROOT ended in, back to the
# rename in 0002. Splitting here is what makes the migration checkout-agnostic.
_ROOT_MARKER = os.sep + 'imagi_projects' + os.sep


def to_relative(apps, schema_editor):
    Project = apps.get_model('ProjectManager', 'Project')
    for project in Project.objects.exclude(project_path='').iterator():
        path = project.project_path
        marker = path.find(_ROOT_MARKER)
        if marker == -1:
            # Outside any recognizable root — keep it absolute.
            project.project_dir = path
        else:
            project.project_dir = path[marker + len(_ROOT_MARKER):]
        project.save(update_fields=['project_dir'])


def to_absolute(apps, schema_editor):
    """Re-expand against the *current* root.

    Not a perfect inverse: the original rows pointed at whichever checkout
    created them, and that information is gone once the path is relative. This
    puts every project under the root configured now, which is the only root
    this installation can actually serve.
    """
    from django.conf import settings

    Project = apps.get_model('ProjectManager', 'Project')
    for project in Project.objects.exclude(project_dir='').iterator():
        stored = project.project_dir
        if os.path.isabs(stored):
            project.project_path = stored
        else:
            project.project_path = os.path.join(settings.PROJECTS_ROOT, stored)
        project.save(update_fields=['project_path'])


class Migration(migrations.Migration):

    dependencies = [
        ('ProjectManager', '0004_project_design_preferences'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='project_dir',
            field=models.CharField(
                blank=True,
                default='',
                max_length=500,
                help_text=(
                    'Project directory, relative to settings.PROJECTS_ROOT. Stored '
                    'relative so a project created in one checkout still resolves in '
                    'another; read it through the project_path property, which joins '
                    'it to the configured root. A path outside that root (a temp '
                    'directory in tests, a legacy row) is stored absolute and returned '
                    'unchanged.'
                ),
            ),
            preserve_default=False,
        ),
        migrations.RunPython(to_relative, to_absolute),
        migrations.RemoveField(
            model_name='project',
            name='project_path',
        ),
    ]
