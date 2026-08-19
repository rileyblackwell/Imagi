from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Build', '0011_agentconversation_goal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agentconversation',
            name='review_status',
            field=models.CharField(
                blank=True,
                choices=[
                    ('', 'None'),
                    ('active', 'Active'),
                    ('input', 'Needs input'),
                    ('ready', 'Ready'),
                    ('failed', 'Failed'),
                    ('accepted', 'Accepted'),
                    ('dismissed', 'Dismissed'),
                ],
                default='',
                max_length=10,
            ),
        ),
    ]
