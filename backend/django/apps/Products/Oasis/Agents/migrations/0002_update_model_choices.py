from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Agents', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agentconversation',
            name='model_name',
            field=models.CharField(choices=[('gpt-4o', 'GPT-4o'), ('gpt-4o-mini', 'GPT-4o Mini'), ('claude-3-7-sonnet-20250219', 'Claude 3.7 Sonnet')], max_length=50),
        ),
    ] 