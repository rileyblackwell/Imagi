# Generated manually for draggable grid redesign

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Builder', '0002_remove_project_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectLayout',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_id', models.CharField(max_length=255)),
                ('layout_data', models.JSONField(default=dict)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_layouts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'project_id')},
                'indexes': [
                    models.Index(fields=['user', 'project_id'], name='Builder_pro_user_id_7f8a3c_idx'),
                ],
            },
        ),
    ]

