"""Give first-build threads made before they carried a goal one.

Without a goal a thread's card names its job from its opening message, which
for a first build is the whole engineering brief. Mirrors PageBrief.goal in
ProjectManager/services/initial_build_service.py.
"""

from django.db import migrations

GOALS = {
    'Initial build — home page': 'Build the landing page — the first thing anyone sees.',
    'Initial build — about page': 'Build the about page — who is behind this business and why it exists.',
    'Initial build — contact page': 'Build the contact page — how a customer reaches this business.',
}


def add_goals(apps, schema_editor):
    AgentConversation = apps.get_model('Build', 'AgentConversation')
    for title, goal in GOALS.items():
        AgentConversation.objects.filter(kind='task', title=title, goal='').update(goal=goal)


class Migration(migrations.Migration):

    dependencies = [
        ('Build', '0017_agentcheckin_details'),
    ]

    operations = [
        migrations.RunPython(add_goals, migrations.RunPython.noop),
    ]
