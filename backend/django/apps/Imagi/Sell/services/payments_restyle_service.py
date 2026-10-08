"""
Fit newly added payment pages into the business's site.

The payments template (payment_templates) arrives in Imagi's neutral look.
Right after an install, this starts one ordinary build thread, the way the
sign-in restyle does (ProjectManager.services.auth_restyle_service), that
rewrites the pages' two open files to match the home page and links the new
pages from the site's navigation. The payment flow itself is locked against
the agents (Build.services.protected_paths), so the thread can't change how
payments work.

Nothing waits on it: the pages work in the default look in the meantime.
Never raises, and starts nothing for a project that hasn't been built yet
(it has no main thread and no home page to match).
"""

import logging

from django.conf import settings
from django.db import close_old_connections

logger = logging.getLogger(__name__)

TASK_TITLE = 'Fit payment pages into your site'
TASK_GOAL = 'Make your new payment pages match your site and link them from it.'

HOME_VIEW_PATH = 'frontend/vuejs/src/apps/home/views/HomeView.vue'


def build_restyle_brief(name: str, routes: list) -> str:
    from apps.Imagi.Build.services.protected_paths import PAYMENTS_RESTYLE_PATHS

    stylesheet, brand = PAYMENTS_RESTYLE_PATHS
    pages = ', '.join(f"'{route}'" for route in routes)
    return f"""Imagi just added prebuilt payment pages to this app: {pages}. Make them look like part of the business's site, and let visitors find them.

The site's design is its home page, '{HOME_VIEW_PATH}'. Read it first and match it: colors, fonts, corner radii, button style, background treatment, and the tone of its copy.

1. Rewrite '{stylesheet}'. It decides everything about how the payment pages look. Start with the tokens on .pay-theme; restyle any rule below them as you need, but keep every class name, because the pages' markup uses all of them. Plain CSS only: no @apply, and no url() to images. Keep it accessible: readable contrast and a visible focus style on buttons.
2. Rewrite the copy in '{brand}' in the home page's voice. Keep its shape and keys.
3. Add a link to {pages} to the site's main navigation (and its footer, if it has one), wherever the other page links live. Change nothing else on those pages.

Everything else under 'frontend/vuejs/src/apps/payments/' and 'backend/django/apps/payments/' is the payment flow Imagi maintains. The file tools refuse to change it, so do not try.

Business name: {name}

When you're done, tell the founder in two plain sentences that their payment pages now match their site and are linked from it, with no file or code names."""


def queue_payments_restyle(project_id: int, user_id: int, routes: list):
    """Stage the thread under the project's main thread and start it."""
    close_old_connections()
    try:
        return _queue(project_id, user_id, routes)
    except Exception:
        logger.exception("Could not start the payment page restyle for project %s", project_id)
        return None
    finally:
        close_old_connections()


def _queue(project_id, user_id, routes):
    from django.contrib.auth import get_user_model
    from apps.Imagi.Build.models import AgentConversation, AgentMessage, SystemPrompt
    from apps.Imagi.Build.services.base_agent import (
        build_message_metadata,
        dispatch_task_refs,
    )
    from apps.Imagi.Build.services.coding_agent import CODING_AGENT_INSTRUCTIONS
    from apps.Imagi.ProjectManager.models import Project
    from apps.Imagi.ProjectManager.services.auth_restyle_service import _start_threads

    project = Project.objects.get(pk=project_id)
    user = get_user_model().objects.get(pk=user_id)
    lead = AgentConversation.objects.filter(
        user=user, project_id=project_id, kind='lead', archived_at__isnull=True
    ).order_by('created_at').first()
    if lead is None:
        return None

    builder = getattr(settings, 'IMAGI_BUILDER', {})
    task = AgentConversation.objects.create(
        user=user,
        model_name=builder.get('DEFAULT_MODEL') or lead.model_name,
        project_id=project_id,
        mode='agent',
        title=TASK_TITLE,
        goal=TASK_GOAL,
        kind='task',
        parent=lead,
        review_status='active',
        queued_prompt=build_restyle_brief(project.name, routes),
    )
    SystemPrompt.objects.create(conversation=task, content=CODING_AGENT_INSTRUCTIONS)
    AgentMessage.objects.create(
        conversation=lead,
        role='assistant',
        content=(
            "You added payments from the Sell console. I've started a thread "
            "that fits the new payment pages into your site."
        ),
        metadata=build_message_metadata(
            dispatched_tasks=dispatch_task_refs(
                [{'conversation_id': task.id, 'title': task.title}]
            )
        ),
    )
    _start_threads(user)
    return task
