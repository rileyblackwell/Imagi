"""
Restyle the prebuilt sign-in and register pages to match a new project's site.

Every project ships with Imagi's prebuilt auth (Build.services.codegen
.prebuilt_apps.auth): the sign-in flow is maintained by Imagi and locked
against the agents, and its whole look lives in two files, the stylesheet
'apps/auth/styles/auth.css' and the copy in 'apps/auth/brand.ts'.

Once the first build lands the home page, this starts one ordinary thread
that rewrites those two files to match it. It runs after the home page
rather than beside it because the home page is the design to match, and in
the background because nothing waits on it: the founder is already in their
app, and the sign-in pages work in the meantime, just in Imagi's neutral
default look. It runs on the first build's model, tier and effort (GPT 6 Luna
on Fast at xhigh; Riley, 2026-10-16), or on the everyday thread model when
that model can't run.

The thread can only change those two files. The brief says so, and the file
tools refuse every other auth path regardless (Build.services.protected_paths),
so a restyle can never touch how sign-in works.
"""

import logging

from django.conf import settings
from django.db import close_old_connections

logger = logging.getLogger(__name__)

TASK_TITLE = 'Restyle sign-in pages'
TASK_GOAL = 'Make your sign-in and register pages match the rest of your site.'

HOME_VIEW_PATH = 'frontend/vuejs/src/apps/home/views/HomeView.vue'
THEME_PATH = 'frontend/vuejs/src/apps/home/styles/theme.css'


def build_restyle_brief(name: str, description: str, design_preferences: str = '') -> str:
    """The thread's brief: match the home page, through the two open files."""
    from apps.Imagi.Build.services.protected_paths import AUTH_RESTYLE_PATHS

    stylesheet, brand = AUTH_RESTYLE_PATHS
    brief = f"""Restyle this project's prebuilt sign-in and register pages ('/auth/signin' and '/auth/register') so they look like part of the business's site.

The site's design is its shared theme, '{THEME_PATH}' (colours, corners, fonts), and its home page, '{HOME_VIEW_PATH}'. Read both first and match them: colors, fonts, corner radii, button style, background treatment, and the tone of the copy.

You may change exactly two files, and you should rewrite both:
- '{stylesheet}' decides everything about how the auth pages look. Start with the tokens on .auth-theme; restyle any rule below them as you need, but keep every class name, because the pages' markup uses all of them. Plain CSS only: no @apply, and no url() to images, since the project has none. If the home page loads a web font, you may @import the same one at the top. Keep it accessible: readable contrast and a visible focus style on inputs and buttons.
- '{brand}' holds the business name and each page's title and subtitle. Keep its shape and keys; rewrite the copy in the home page's voice.

Everything else under 'frontend/vuejs/src/apps/auth/' and 'backend/django/apps/auth/' is the sign-in flow Imagi maintains. The file tools refuse to change it, so do not try, and do not touch any other file.

Business name: {name}

What it does:
{description}"""
    design = (design_preferences or '').strip()
    if design:
        brief += f"\n\nDesign & style preferences (from the founder):\n{design}"
    brief += (
        "\n\nWhen you're done, tell the founder in two plain sentences that "
        "their sign-in and register pages now match their site, with no file "
        "or code names."
    )
    return brief


def restyle_model(builder, lead):
    """The model, OpenAI tier and effort the restyle thread runs on.

    The first build's own (INITIAL_BUILD_MODEL), unless it is a GPT model
    and there is no OpenAI key, in which case the everyday thread model.
    """
    from apps.Imagi.Build.services.api_keys import read_api_key
    from apps.Imagi.Build.services.models_service import get_model_provider

    model = builder.get('INITIAL_BUILD_MODEL')
    if model and not (get_model_provider(model) == 'openai' and not read_api_key('OPENAI_KEY')):
        return (
            model,
            builder.get('INITIAL_BUILD_SERVICE_TIER') or None,
            builder.get('INITIAL_BUILD_REASONING_EFFORT') or None,
        )
    return builder.get('DEFAULT_MODEL') or lead.model_name, None, None


def queue_auth_restyle(project_id: int, user_id: int):
    """Stage the restyle thread under the project's main thread and start it.

    Called from the first build once the home page has landed. Never raises:
    a restyle that cannot start leaves working pages in the default look,
    which is no reason to disturb the build that called it. Returns the
    thread's conversation, or None when none was started.
    """
    close_old_connections()
    try:
        return _queue_auth_restyle(project_id, user_id)
    except Exception:
        logger.exception(
            "Could not start the sign-in page restyle for project %s", project_id
        )
        return None
    finally:
        close_old_connections()


def _queue_auth_restyle(project_id, user_id):
    from django.contrib.auth import get_user_model
    from apps.Imagi.Build.models import AgentConversation, AgentMessage, SystemPrompt
    from apps.Imagi.Build.services.base_agent import (
        build_message_metadata,
        dispatch_task_refs,
    )
    from apps.Imagi.Build.services.coding_agent import CODING_AGENT_INSTRUCTIONS
    from ..models import Project

    project = Project.objects.get(pk=project_id)
    user = get_user_model().objects.get(pk=user_id)
    lead = AgentConversation.objects.filter(
        user=user, project_id=project_id, kind='lead', archived_at__isnull=True
    ).order_by('created_at').first()
    if lead is None:
        logger.warning(
            "No main thread for project %s; not restyling its sign-in pages",
            project_id,
        )
        return None

    model, service_tier, effort = restyle_model(getattr(settings, 'IMAGI_BUILDER', {}), lead)
    task = AgentConversation.objects.create(
        user=user,
        model_name=model,
        service_tier=service_tier or '',
        reasoning_effort=effort or '',
        project_id=project_id,
        mode='agent',
        title=TASK_TITLE,
        goal=TASK_GOAL,
        kind='task',
        parent=lead,
        review_status='active',
        queued_prompt=build_restyle_brief(
            project.name,
            project.description,
            getattr(project, 'design_preferences', ''),
        ),
    )
    SystemPrompt.objects.create(conversation=task, content=CODING_AGENT_INSTRUCTIONS)

    # Shown in the main thread the way any dispatch is, with its thread card.
    AgentMessage.objects.create(
        conversation=lead,
        role='assistant',
        content=(
            "Your home page is ready. I've started a thread that restyles your "
            "sign-in and register pages to match it."
        ),
        metadata=build_message_metadata(
            dispatched_tasks=dispatch_task_refs(
                [{'conversation_id': task.id, 'title': task.title}]
            )
        ),
    )

    _start_threads(user)
    logger.info(
        "Started the sign-in page restyle for project %s (thread %s)",
        project_id,
        task.id,
    )
    return task


def _start_threads(user):
    """Start the staged thread now rather than at the scheduler's next pass.

    Called from the first build's own thread, which has no event loop. A run
    lives on the loop that started it, so the start gets a thread and a loop
    of its own that stay up until the runs it started have ended. (Started
    through async_to_sync instead, the run died with that call's loop the
    moment it returned, and the thread sat claimed, doing nothing, until the
    scheduler's staleness window let it start again ten minutes later.)
    """
    import asyncio
    import threading

    from apps.Imagi.Build.services import detached_runs
    from apps.Imagi.Build.services.thread_scheduler import start_waiting_threads

    async def start_and_wait():
        await start_waiting_threads(user)
        loop = asyncio.get_running_loop()
        while True:
            mine = [t for t in list(detached_runs._running) if t.get_loop() is loop]
            if not mine:
                return
            await asyncio.gather(*mine, return_exceptions=True)

    def run():
        try:
            asyncio.run(start_and_wait())
        except Exception as e:
            # Staged work is still picked up the next time the scheduler runs.
            logger.warning("Could not start the restyle thread right away: %s", e)
        finally:
            close_old_connections()

    threading.Thread(target=run, name='auth-restyle', daemon=True).start()
