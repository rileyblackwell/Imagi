from django.db import migrations, models


class Migration(migrations.Migration):
    """A finished subagent files a 'done' check-in.

    Its work is already merged, so the card is a notification rather than a
    decision — see AgentCheckIn's docstring.
    """

    dependencies = [
        ('Build', '0012_review_status_failed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agentcheckin',
            name='kind',
            field=models.CharField(
                choices=[
                    ('done', 'Complete'),
                    ('ready', 'Ready for review'),
                    ('question', 'Question'),
                    ('error', 'Error'),
                ],
                max_length=10,
            ),
        ),
    ]
