# Generated for GPT 5.6 suite (Sol, Terra, Luna) model choices update.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Agents', '0002_alter_agentconversation_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agentconversation',
            name='model_name',
            field=models.CharField(
                choices=[
                    ('gpt-5.6-sol', 'GPT 5.6 Sol'),
                    ('gpt-5.6-terra', 'GPT 5.6 Terra'),
                    ('gpt-5.6-luna', 'GPT 5.6 Luna'),
                ],
                max_length=50,
            ),
        ),
    ]
