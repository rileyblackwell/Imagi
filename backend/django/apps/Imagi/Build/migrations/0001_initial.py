"""
Initial migration for the Build app.

Build replaces the old Agents and Builder apps and keeps their existing
database tables (via db_table overrides). Production databases already
contain those tables, so the CreateModel operations are applied to
migration state only; the actual tables are created by a guarded step
that skips any table that already exists.
"""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

# Creation order matters: models with foreign keys must come after their
# targets so the guarded table creation can run top to bottom.
MODEL_NAMES = [
    'AgentConversation',
    'AgentMessage',
    'Conversation',
    'Page',
    'Message',
    'SystemPrompt',
    'ProjectLayout',
]


def create_missing_tables(apps, schema_editor):
    existing_tables = set(schema_editor.connection.introspection.table_names())
    for model_name in MODEL_NAMES:
        model = apps.get_model('Build', model_name)
        if model._meta.db_table not in existing_tables:
            schema_editor.create_model(model)


def drop_tables(apps, schema_editor):
    existing_tables = set(schema_editor.connection.introspection.table_names())
    for model_name in reversed(MODEL_NAMES):
        model = apps.get_model('Build', model_name)
        if model._meta.db_table in existing_tables:
            schema_editor.delete_model(model)


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='AgentConversation',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                        ('model_name', models.CharField(choices=[('gpt-5.6-sol', 'GPT 5.6 Sol'), ('gpt-5.6-terra', 'GPT 5.6 Terra'), ('gpt-5.6-luna', 'GPT 5.6 Luna')], max_length=50)),
                        ('provider', models.CharField(choices=[('openai', 'OpenAI')], default='openai', max_length=20)),
                        ('project_id', models.IntegerField(blank=True, null=True)),
                        ('title', models.CharField(blank=True, default='', max_length=120)),
                        ('mode', models.CharField(choices=[('chat', 'Chat'), ('agent', 'Agent')], default='chat', max_length=10)),
                        ('archived_at', models.DateTimeField(blank=True, null=True)),
                        ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agent_conversations', to=settings.AUTH_USER_MODEL)),
                    ],
                    options={
                        'db_table': 'Agents_agentconversation',
                        'ordering': ['-updated_at'],
                    },
                ),
                migrations.CreateModel(
                    name='AgentMessage',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('role', models.CharField(choices=[('user', 'User'), ('assistant', 'Assistant'), ('system', 'System')], max_length=10)),
                        ('content', models.TextField()),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='Build.agentconversation')),
                    ],
                    options={
                        'db_table': 'Agents_agentmessage',
                        'ordering': ['created_at'],
                    },
                ),
                migrations.CreateModel(
                    name='Conversation',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('project_id', models.IntegerField(null=True)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conversations', to=settings.AUTH_USER_MODEL)),
                    ],
                    options={
                        'db_table': 'Builder_conversation',
                    },
                ),
                migrations.CreateModel(
                    name='Page',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('filename', models.CharField(max_length=255)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pages', to='Build.conversation')),
                    ],
                    options={
                        'db_table': 'Builder_page',
                        'unique_together': {('conversation', 'filename')},
                    },
                ),
                migrations.CreateModel(
                    name='Message',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('role', models.CharField(choices=[('user', 'User'), ('assistant', 'Assistant'), ('system', 'System')], max_length=10)),
                        ('content', models.TextField()),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='Build.conversation')),
                        ('page', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='Build.page')),
                    ],
                    options={
                        'db_table': 'Builder_message',
                    },
                ),
                migrations.CreateModel(
                    name='SystemPrompt',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('content', models.TextField()),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                        ('conversation', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='system_prompt', to='Build.agentconversation')),
                    ],
                    options={
                        'db_table': 'Agents_systemprompt',
                    },
                ),
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
                        'db_table': 'Builder_projectlayout',
                        'indexes': [models.Index(fields=['user', 'project_id'], name='Builder_pro_user_id_0f5205_idx')],
                        'unique_together': {('user', 'project_id')},
                    },
                ),
            ],
            database_operations=[],
        ),
        migrations.RunPython(create_missing_tables, drop_tables),
    ]
