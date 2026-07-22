# Enforce the single-lead invariant at the database: at most one unarchived
# kind='lead' conversation per (user, project). The API's check-then-create is
# not atomic, so concurrent creates (multi-worker gunicorn, two tabs) could
# otherwise both insert a live lead.

from django.db import migrations, models
from django.utils import timezone


def archive_duplicate_live_leads(apps, schema_editor):
    """Keep the oldest live lead per (user, project); archive the rest.

    Databases that ran the pre-constraint code may already hold duplicates,
    which would make adding the partial unique index fail.
    """
    AgentConversation = apps.get_model('Build', 'AgentConversation')
    seen = set()
    duplicates = []
    for row in AgentConversation.objects.filter(
        kind='lead', archived_at__isnull=True
    ).order_by('created_at', 'id'):
        key = (row.user_id, row.project_id)
        if key in seen:
            duplicates.append(row.id)
        else:
            seen.add(key)
    if duplicates:
        AgentConversation.objects.filter(id__in=duplicates).update(
            archived_at=timezone.now()
        )


class Migration(migrations.Migration):

    dependencies = [
        ('Build', '0008_agentconversation_kind_agentconversation_parent_and_more'),
    ]

    operations = [
        migrations.RunPython(
            archive_duplicate_live_leads, migrations.RunPython.noop
        ),
        migrations.AddConstraint(
            model_name='agentconversation',
            constraint=models.UniqueConstraint(
                condition=models.Q(archived_at__isnull=True, kind='lead'),
                fields=('user', 'project_id'),
                name='one_live_lead_per_project',
            ),
        ),
    ]
