from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Agents', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agentconversation',
            name='model_name',
            field=models.CharField(choices=[
                ('gpt-4.1', 'GPT-4.1'),
                ('gpt-4.1-nano', 'GPT-4.1 Nano'),
                ('claude-3-7-sonnet-20250219', 'Claude 3.7 Sonnet')
            ], max_length=50),
        ),
    ] 