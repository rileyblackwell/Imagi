from django.db import migrations, models


class Migration(migrations.Migration):
    """A dispatched task carries an overview.

    A few sentences, in the owner's words, on what the subagent is about to do
    — the body of its card in the main thread while the run is live. See
    AgentConversation.overview.
    """

    dependencies = [
        ('Build', '0013_check_in_done_kind'),
    ]

    operations = [
        migrations.AddField(
            model_name='agentconversation',
            name='overview',
            field=models.TextField(blank=True, default=''),
        ),
    ]
