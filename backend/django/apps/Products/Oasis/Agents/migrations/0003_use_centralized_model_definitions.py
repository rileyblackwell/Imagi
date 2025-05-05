from django.db import migrations, models
import apps.Products.Oasis.Builder.services.models_service as model_defs


class Migration(migrations.Migration):

    dependencies = [
        ('Agents', '0002_update_model_choices'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agentconversation',
            name='model_name',
            field=models.CharField(choices=model_defs.get_model_choices(), max_length=50),
        ),
        migrations.AlterField(
            model_name='agentconversation',
            name='provider',
            field=models.CharField(choices=model_defs.get_provider_choices(), default=model_defs.get_default_provider(), max_length=20),
        ),
    ] 