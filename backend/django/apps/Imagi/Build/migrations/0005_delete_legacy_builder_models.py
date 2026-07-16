"""
Remove the legacy Builder workspace models (Conversation, Page, Message).

These predate the agent-based workspace: no routed view or service reads or
writes them anymore (the live conversation models are AgentConversation /
AgentMessage). Models are deleted child-first so foreign keys are dropped
with their tables.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("Build", "0004_projectfile"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Message",
        ),
        migrations.DeleteModel(
            name="Page",
        ),
        migrations.DeleteModel(
            name="Conversation",
        ),
    ]
