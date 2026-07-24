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

from django.conf import settings
from django.db import close_old_connections
from django.utils import timezone

logger = logging.getLogger(__name__)


def build_initial_prompt(name: str, description: str, design_preferences: str = "") -> str:
    """Compose the first build prompt from the founder's inputs.

    Kept intentionally short: the framing, the freedom to build whatever the
    business needs, the design direction, and the guardrails (keep auth, no
    payments) all live in the initial-build system prompt
    (coding_agent.INITIAL_BUILD_INSTRUCTIONS). This message just hands over the
    business the agent is building.
    """
    prompt = f"""This is the first build of a brand-new project — build the first version of this business's web app.

Business name: {name}

Business description (written by the founder):
{description}"""

    design = (design_preferences or "").strip()
    if design:
        prompt += f"\n\nDesign & style preferences (from the founder):\n{design}"

    prompt += (
        "\n\nBuild a tailored, polished first version that fits this business, "
        "following your design direction. When you're done, briefly summarize "
        "what you built."
    )
    return prompt


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
        from apps.Imagi.Build.services.coding_agent import INITIAL_BUILD_INSTRUCTIONS

        project = Project.objects.get(pk=project_id)
        user = get_user_model().objects.get(pk=user_id)

        builder = getattr(settings, 'IMAGI_BUILDER', {})

        service = ImagiAgentService()
        conversation = service.create_conversation(
            user,
            service.model,
            project_id=project_id,
            title='Initial build',
            kind='initial_build',
            system_prompt=INITIAL_BUILD_INSTRUCTIONS,
        )

        result = service.process(
            user_input=build_initial_prompt(
                project.name,
                project.description,
                getattr(project, 'design_preferences', ''),
            ),
            user=user,
            project_id=project_id,
            conversation_id=conversation.id,
            max_turns=builder.get('INITIAL_BUILD_MAX_TURNS'),
            cost_budget_usd=builder.get('INITIAL_BUILD_COST_BUDGET_USD'),
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
