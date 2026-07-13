"""
Initial AI build service.

When a user creates a project (their business), the business name and
description they provided become the first build prompt for the coding
agent. The build runs in a background thread so project creation stays
fast; by the time the user enters build mode the workspace already has a
tailored starting point instead of the generic scaffold.

Build progress is tracked on the existing Project.generation_status field
('generating' -> 'completed'/'failed'), and the run is persisted as an
"Initial build" agent conversation so it shows up in the workspace chat.
"""

import logging
import threading

from django.db import close_old_connections
from django.utils import timezone

logger = logging.getLogger(__name__)


def build_initial_prompt(name: str, description: str) -> str:
    """Compose the first build prompt from the business name and description."""
    return f"""You are performing the very first build of a brand-new project the user just created on Imagi. Nothing custom has been built yet — the project contains only Imagi's default scaffold (home and auth apps).

Business name: {name}

Business description (written by the founder):
{description}

Using this description, build the first version of the business's web application so the founder sees a tailored starting point — not a generic scaffold — when they open the workspace:

1. Rework the home app's landing page around this business: a clear hero (business name and what it does), sections covering its offering and intended customers, and a call to action that matches the sales approach in the description.
2. Update titles, headings, and placeholder copy that still reference the scaffold so they reflect the business.
3. If the description clearly calls for one or two more simple pages (for example an About or Pricing page), create them and wire up their routes.

Keep the scope tight: this is a strong starting point, not a finished product. Do not touch the auth app beyond copy tweaks, and do not invent features the description doesn't support. Do not build any payment or checkout functionality even if the description mentions selling — the founder adds secure, prebuilt payment pages later from their Sell workspace. When you finish, briefly summarize what you built — the founder will read it as the first message in their workspace."""


def start_initial_build(project, user) -> bool:
    """Kick off the initial AI build for a freshly created project.

    Marks the project as 'generating' synchronously (so the status is
    already correct when the create response returns) and runs the agent
    in a daemon thread. Returns False when no AI provider is configured.
    """
    from apps.Imagi.Build.services.base_agent import OPENAI_API_KEY

    if not OPENAI_API_KEY:
        logger.warning(
            "OPENAI_KEY not configured - skipping initial AI build for project %s",
            project.pk,
        )
        return False

    from ..models import Project

    Project.objects.filter(pk=project.pk).update(generation_status='generating')
    project.generation_status = 'generating'

    thread = threading.Thread(
        target=_run_initial_build,
        args=(project.pk, user.pk),
        name=f"initial-build-{project.pk}",
        daemon=True,
    )
    thread.start()
    logger.info("Initial AI build started in background for project %s", project.pk)
    return True


def _run_initial_build(project_id: int, user_id: int) -> None:
    """Thread body: run the coding agent with the business description prompt."""
    close_old_connections()
    from ..models import Project

    try:
        from django.contrib.auth import get_user_model
        from apps.Imagi.Build.services.base_agent import ImagiAgentService

        project = Project.objects.get(pk=project_id)
        user = get_user_model().objects.get(pk=user_id)

        service = ImagiAgentService()
        conversation = service.create_conversation(
            user,
            service.model,
            project_id=project_id,
            mode='agent',
            title='Initial build',
        )

        result = service.process_agent(
            user_input=build_initial_prompt(project.name, project.description),
            user=user,
            project_id=project_id,
            conversation_id=conversation.id,
        )

        if result.get('success'):
            Project.objects.filter(pk=project_id).update(
                generation_status='completed',
                last_generated_at=timezone.now(),
            )
            logger.info(
                "Initial AI build completed for project %s (files changed: %s)",
                project_id,
                result.get('files_changed'),
            )
        else:
            Project.objects.filter(pk=project_id).update(generation_status='failed')
            logger.error(
                "Initial AI build failed for project %s: %s",
                project_id,
                result.get('error'),
            )
    except Exception:
        logger.exception("Initial AI build crashed for project %s", project_id)
        try:
            Project.objects.filter(pk=project_id).update(generation_status='failed')
        except Exception:
            pass
    finally:
        close_old_connections()
