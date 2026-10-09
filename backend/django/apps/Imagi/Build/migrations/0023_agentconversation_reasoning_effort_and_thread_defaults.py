from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Build", "0022_agentconversation_fast_mode"),
    ]

    operations = [
        migrations.AddField(
            model_name="agentconversation",
            name="reasoning_effort",
            field=models.CharField(blank=True, default="", max_length=10),
        ),
        migrations.AddField(
            model_name="agentconversation",
            name="thread_model_name",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
        migrations.AddField(
            model_name="agentconversation",
            name="thread_reasoning_effort",
            field=models.CharField(blank=True, default="", max_length=10),
        ),
    ]
