from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Build", "0021_claude_model_lineup"),
    ]

    operations = [
        migrations.AddField(
            model_name="agentconversation",
            name="fast_mode",
            field=models.BooleanField(default=False),
        ),
    ]
