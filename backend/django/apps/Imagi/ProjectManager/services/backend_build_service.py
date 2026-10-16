"""
Build a new project's backend alongside its first pages, then connect them.

The first build's page threads write presentational pages: each owns one
file and calls no API, so every page can land on its own, fast, and the
founder sees their app first (Riley, 2026-10-16). The server side of the
app's first features is built at the same time, by one more thread:

1. As soon as the pages are planned, a backend thread starts. It reads the
   founder's brief and the page plan, works out what the app must store and
   do on the server, and builds it as Django apps with an API under
   /api/v1/, plus a typed client for the frontend. It leaves the pages alone,
   since they are being written at the same moment.
2. Once every page has landed, the same thread gets a second job: connect
   the pages to the API it built. It is placed after the first on the
   thread's schedule (scheduling.schedule_work), so it starts only when the
   backend has landed too, and its run forks a copy of the app that already
   holds every page.

Sign-in and registration are not part of this: every project ships Imagi's
prebuilt auth, front and back, which the agents can't change.

Like the pages, the thread runs on the first build's model, tier and effort
(GPT 6 Luna on Fast at xhigh), or the everyday thread model when that one
can't run (auth_restyle_service.restyle_model). It is started right away
rather than waiting for a slot, because the page threads fill the user's
slots for the whole first build, and the backend is meant to be built while
they run.
"""

import logging

from django.conf import settings
from django.db import close_old_connections
from django.utils import timezone

logger = logging.getLogger(__name__)

TASK_TITLE = 'Build the backend'
TASK_GOAL = "Build your app's server side: what it stores and the API its pages use."

AUTH_STORE = '@/apps/auth/stores'
API_CLIENT = '@/shared/services/api'


def _page_lines(pages) -> str:
    return '\n'.join(
        f"- '{p.route}' ({p.view_path}): {p.summary}" for p in pages
    )


def build_backend_brief(name, description, app_details='', pages=()) -> str:
    """The backend thread's first job: the server side of the first version."""
    brief = f"""Build the backend for the first version of this app, while other threads build its pages.

App name: {name}

What it does (from the founder):
{description}"""
    details = (app_details or '').strip()
    if details:
        brief += f"\n\nHow the app should work (from the founder):\n{details}"
    if pages:
        brief += f"\n\nThe pages being built now:\n{_page_lines(pages)}"
    brief += f"""

Work out what the app must store and do on the server for these pages to really work (for example bookings, orders or messages from a form) and build it in backend/django: a Django app per area under apps/, with models, migrations, serializers, the business logic in services, and views. Mount each app's API under /api/v1/<app>/ in api/v1/url.py and add the app to INSTALLED_APPS. Check it with check_backend. Then write a typed client for each API in frontend/vuejs/src/apps/<app>/services/, on the shared client '{API_CLIENT}', which already sends the signed-in user's token.

Sign-in and registration are prebuilt, front and back (/api/v1/auth/), and can't be changed. Use request.user, and require sign-in for anything that belongs to a user.

Don't change the pages: they are being written right now, and you'll connect them to your API once they're in. If the app needs nothing on the server beyond sign-in, change nothing and say so."""
    return brief


def build_wiring_brief(pages) -> str:
    """The backend thread's second job, once the pages are in."""
    return f"""The pages are in. Connect the ones that use what you built to your API, through the clients you wrote: real data in place of made-up examples, forms that save, loading and error states, and sign-in where your API requires it (the auth store is useAuthStore from '{AUTH_STORE}'; send a signed-out visitor to '/auth/signin?redirect=<the page's path>'). Keep each page's design and copy, and change only what connecting it needs. Then try the main flow once in the preview, signed in.

The pages:
{_page_lines(pages)}

If you built no API, change nothing and say there's nothing to connect."""


def queue_backend_build(project_id: int, user_id: int, pages):
    """Start the backend thread under the project's main thread.

    Called by the first build once its pages are planned. Never raises: the
    pages are worth having without a backend. Returns the thread's
    ThreadTask, or None when none was started.
    """
    close_old_connections()
    try:
        return _queue_backend_build(project_id, user_id, pages)
    except Exception:
        logger.exception("Could not start the backend build for project %s", project_id)
        return None
    finally:
        close_old_connections()


def _queue_backend_build(project_id, user_id, pages):
    from django.contrib.auth import get_user_model
    from apps.Imagi.Build.models import AgentConversation, AgentMessage, SystemPrompt
    from apps.Imagi.Build.services.base_agent import (
        build_message_metadata,
        dispatch_task_refs,
    )
    from apps.Imagi.Build.services.coding_agent import CODING_AGENT_INSTRUCTIONS
    from apps.Imagi.Build.services.scheduling import schedule_work
    from ..models import Project
    from .auth_restyle_service import restyle_model

    project = Project.objects.get(pk=project_id)
    user = get_user_model().objects.get(pk=user_id)
    lead = AgentConversation.objects.filter(
        user=user, project_id=project_id, kind='lead', archived_at__isnull=True
    ).order_by('created_at').first()
    if lead is None:
        logger.warning("No main thread for project %s; not building its backend", project_id)
        return None

    model, service_tier, effort = restyle_model(getattr(settings, 'IMAGI_BUILDER', {}), lead)
    thread = AgentConversation.objects.create(
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
        # Claimed for the run started below: the thread scheduler starts
        # staged work nobody is running, and this is about to run here.
        run_started_at=timezone.now(),
    )
    SystemPrompt.objects.create(conversation=thread, content=CODING_AGENT_INSTRUCTIONS)
    task = schedule_work(
        lead=lead, thread=thread, placement='new',
        brief=build_backend_brief(
            project.name, project.description, getattr(project, 'app_details', ''), pages,
        ),
        reason="Builds the server side while the pages are written",
    )

    AgentMessage.objects.create(
        conversation=lead,
        role='assistant',
        content=(
            "I've also started a thread on your app's backend: what it stores and "
            "the API its pages use. Once your pages are in, it connects them."
        ),
        metadata=build_message_metadata(
            dispatched_tasks=dispatch_task_refs(
                [{'conversation_id': thread.id, 'title': thread.title}]
            )
        ),
    )

    thread.refresh_from_db()
    _run_now(user, thread)
    logger.info("Started the backend build for project %s (thread %s)", project_id, thread.id)
    return task


def queue_page_wiring(project_id: int, user_id: int, backend_task, pages):
    """Give the backend thread its second job: connect the landed pages.

    Called by the first build once every page has finished. Held on the
    schedule until the backend's own job lands, then started like any
    thread's work. Skipped when there is nothing to connect: no page landed,
    the backend thread built nothing, or its work failed. Never raises.
    Returns the ThreadTask, or None.
    """
    close_old_connections()
    try:
        return _queue_page_wiring(user_id, backend_task, pages)
    except Exception:
        logger.exception("Could not queue connecting the pages for project %s", project_id)
        return None
    finally:
        close_old_connections()


def _queue_page_wiring(user_id, backend_task, pages):
    from django.contrib.auth import get_user_model
    from apps.Imagi.Build.services.scheduling import STUCK_STATUSES, schedule_work

    if backend_task is None or not pages:
        return None
    backend_task.refresh_from_db()
    if backend_task.status in STUCK_STATUSES:
        return None
    if backend_task.status == 'done' and not (backend_task.result or {}).get('files'):
        return None

    thread = backend_task.thread
    task = schedule_work(
        lead=backend_task.coordinator, thread=thread, placement='append',
        brief=build_wiring_brief(pages),
        reason="Connects the pages once they and the backend are in",
        depends_on=[] if backend_task.status == 'done' else [backend_task],
    )
    if task.status == 'queued':
        from .auth_restyle_service import _start_threads

        _start_threads(get_user_model().objects.get(pk=user_id))
    return task


def _run_now(user, thread):
    """Run the thread's staged work now, on a loop of its own.

    The same run the thread scheduler would start, minus the wait for a free
    slot. The loop stays up until every run it started has ended, including
    the follow-up the thread scheduler starts there when this one ends (see
    auth_restyle_service._start_threads).
    """
    import asyncio
    import threading

    from apps.Imagi.Build.services import detached_runs
    from apps.Imagi.Build.services.thread_scheduler import _thread_events

    item = {
        'conversation_id': thread.id,
        'brief': thread.queued_prompt,
        'model': thread.model_name,
        'project_id': thread.project_id,
    }

    async def run_and_wait():
        detached_runs.start_detached_run(
            lambda: _thread_events(user, item), user=user, conversation_id=thread.id,
        )
        loop = asyncio.get_running_loop()
        while True:
            mine = [t for t in list(detached_runs._running) if t.get_loop() is loop]
            if not mine:
                return
            await asyncio.gather(*mine, return_exceptions=True)

    def run():
        try:
            asyncio.run(run_and_wait())
        except Exception as e:
            logger.warning("The backend thread %s stopped: %s", thread.id, e)
        finally:
            close_old_connections()

    threading.Thread(target=run, name=f'backend-build-{thread.id}', daemon=True).start()
