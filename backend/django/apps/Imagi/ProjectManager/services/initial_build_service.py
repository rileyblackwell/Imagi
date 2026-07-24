"""
Initial AI build service.

When a user creates a project (their business), the name, description and any
style preferences they provided become the first build prompt for the coding
agent. The build runs in a background thread so project creation stays
fast; by the time the user enters build mode the workspace already has a
tailored starting point instead of the generic scaffold.

It runs the same way every other piece of building work does: the project's
main thread (the 'lead' conversation) opens with the founder's brief and
dispatches it to a background subagent (a 'task' conversation). That gives
the first build the machinery every task already has — it builds in its own
git worktree, so the project the preview serves is never half-written, and
its result is merged in one step when it is finished and sound.

The build is bounded by wall-clock time, not by how much it manages to build:
the founder is waiting on it, so the whole thing — first run plus any repair
run — shares one deadline (IMAGI_BUILDER['INITIAL_BUILD_TIME_BUDGET_S'], sized
so the founder waits about half a minute) and ships whatever is finished and
sound when that runs out. This degrades safely because the project already
holds a working home + auth scaffold the moment it is created: a build that
runs short means less tailoring, never a broken app.

That deadline is what sets the scope. Half a minute buys one good write, so the
subagent is pointed at exactly one thing (coding_agent.INITIAL_BUILD_GUIDANCE):
rewrite the home page as a single self-contained component, with the prebuilt
auth app's sign-in and register pages wired into its header and calls to
action. Everything else a web app needs — the Vue and Django scaffolding, the
auth app itself — is already on disk before this runs.

"Sound" is enforced, not hoped for: a build cut short by a cap can leave a page
importing a component it never wrote, and Vite serves that as a "Failed to
resolve import" error instead of the app. Before the worktree is merged, the
frontend's import graph is checked; a build with dangling references gets a
follow-up repair run from whatever time is left, and one that still doesn't
resolve is never merged — the project keeps its clean, working scaffold. The
one-file scope is the first line of that defense: a page that imports nothing
it wrote itself cannot dangle in the first place.

A third check asks whether the page the build wrote still links to the sign-in
and register pages, since a wholesale rewrite can quietly drop them and leave
auth nothing points at. That one earns a repair run but never costs the build:
a page that loads and is hard to sign into still beats the scaffold, so an
unrepaired one is merged anyway.

Build progress is tracked on the existing Project.generation_status field
('generating' -> 'completed'/'failed').
"""

import logging
import threading
import time

from django.conf import settings
from django.db import close_old_connections
from django.utils import timezone

logger = logging.getLogger(__name__)

# Shown in the workspace as the subagent's thread name.
TASK_TITLE = 'Initial build'

# The lead thread's one-line acknowledgement, mirroring how it reports any
# dispatch it makes. Written directly rather than generated: the lead's only
# job here is to hand the brief over, and a model call to produce one fixed
# sentence would just add latency and cost to project creation.
LEAD_ACK = (
    "On it — I've kicked off a subagent to build the first version of your app. "
    "You can watch it work in its thread; I'll let you know when it's done."
)


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
        "\n\nBuild a tailored, polished home page that fits this business, "
        "following your design direction, and wire the prebuilt sign-in and "
        "register pages into it. When you're done, briefly summarize what you "
        "built."
    )
    return prompt


def build_repair_prompt(problems, router_problems=(), auth_problems=()) -> str:
    """Ask the subagent to fix what is keeping its build from being applied.

    Covers the two blocking defects — references to files that were never
    created, and an app router that stopped handing its routes to the root
    router — plus the one advisory defect: a home page that no longer links to
    the prebuilt sign-in and register pages.
    """
    from apps.Imagi.Build.services.frontend_integrity import (
        describe_auth_link_problems,
        describe_router_contract_problems,
        describe_unresolved_imports,
    )

    sections = ["Your build is not finished and cannot be shown to the founder yet."]

    if problems:
        sections.append(
            "The frontend references files that do not exist, so the app fails "
            "to load with a \"Failed to resolve import\" error. Fix every one "
            f"of these:\n\n{describe_unresolved_imports(problems)}\n\n"
            "For each: either create the missing file properly, or remove the "
            "reference and whatever depends on it (including its route entry). "
            "If it is an image or media file, remove it — this project has no "
            "image assets and you cannot create them; use a CSS gradient, a "
            "colored block, or an inline <svg> instead."
        )

    if router_problems:
        sections.append(
            "An app's router module no longer hands its routes to the project's "
            "root router, which means every page 404s — including the home page:"
            f"\n\n{describe_router_contract_problems(router_problems)}\n\n"
            "Restore the contract: the app's 'router/index.ts' must import its "
            "view components and export a plain routes array, like\n"
            "    import type { RouteRecordRaw } from 'vue-router'\n"
            "    import HomeView from '../views/HomeView.vue'\n"
            "    const routes: RouteRecordRaw[] = [\n"
            "      { path: '/', name: 'home-view', component: HomeView }\n"
            "    ]\n"
            "    export { routes }\n"
            "Do NOT call createRouter or createWebHistory in an app router — "
            "'frontend/vuejs/src/router' already does that and globs up every "
            "app's routes."
        )

    if auth_problems:
        sections.append(
            "Your home page dropped the links to the project's prebuilt "
            "sign-in and register pages, so there is now no way into them:"
            f"\n\n{describe_auth_link_problems(auth_problems)}\n\n"
            "Add them back to the page you wrote, styled to match it: a "
            "'Sign in' <router-link> to '/auth/signin' in the header, and a "
            "create-account <router-link> to '/auth/register' as the header's "
            "and the hero's call to action (word it for this business). Keep "
            "both paths exact, and leave 'frontend/vuejs/src/apps/auth/' "
            "itself untouched — those pages already work."
        )

    sections.append(
        "Do not start any new pages or features — this run is only to make what "
        "you already built load cleanly. Then summarize what you fixed."
    )
    return "\n\n".join(sections)


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


def _ensure_lead_conversation(service, user, project_id, model):
    """The project's main thread, created if this is its first use.

    The workspace converges on the same row (its create endpoint returns an
    existing live lead rather than making a second one), so opening it here
    means the founder finds the first build already in their main thread
    instead of an empty workspace.
    """
    from apps.Imagi.Build.models import AgentConversation

    lead = AgentConversation.objects.filter(
        user=user, project_id=project_id, kind='lead', archived_at__isnull=True
    ).order_by('created_at').first()
    if lead is not None:
        return lead
    return service.create_conversation(
        user, model, project_id=project_id, title='Main thread', kind='lead'
    )


def _open_lead_thread(service, lead, prompt, task):
    """Record the dispatch in the main thread, the way a real one reads.

    The founder's brief becomes the opening user message and the lead's
    acknowledgement carries a reference to the subagent's thread, so the
    transcript and its "watch the subagent" link match every later dispatch.
    """
    from apps.Imagi.Build.services.base_agent import (
        build_message_metadata,
        dispatch_task_refs,
    )

    service.add_user_message(lead, prompt)
    service.add_assistant_message(
        lead,
        LEAD_ACK,
        build_message_metadata(
            dispatched_tasks=dispatch_task_refs(
                [{'conversation_id': task.id, 'title': task.title}]
            )
        ),
    )


def _create_build_task(user, lead, project_id, model, prompt):
    """Create the subagent conversation the first build runs in.

    An ordinary kind='task' child of the lead: it gets a git worktree of its
    own, auto-applies when it finishes cleanly, and reports back through the
    lead's check-in queue — all of it existing machinery.
    """
    from apps.Imagi.Build.models import AgentConversation, SystemPrompt
    from apps.Imagi.Build.services.coding_agent import INITIAL_BUILD_INSTRUCTIONS

    task = AgentConversation.objects.create(
        user=user,
        model_name=model,
        project_id=project_id,
        mode='agent',
        title=TASK_TITLE,
        kind='task',
        parent=lead,
        review_status='active',
        queued_prompt=prompt,
    )
    SystemPrompt.objects.create(
        conversation=task, content=INITIAL_BUILD_INSTRUCTIONS
    )
    return task


def _run_initial_build(project_id: int, user_id: int) -> None:
    """Thread body: dispatch the first build to a subagent and land its work."""
    close_old_connections()
    from ..models import Project

    try:
        from django.contrib.auth import get_user_model
        from apps.Imagi.Build.services.base_agent import ImagiAgentService

        project = Project.objects.get(pk=project_id)
        user = get_user_model().objects.get(pk=user_id)

        builder = getattr(settings, 'IMAGI_BUILDER', {})
        model = builder.get('INITIAL_BUILD_MODEL') or builder.get('DEFAULT_MODEL')

        # agent_kind pins the first-build persona (its prompt and design
        # direction) onto what is otherwise a plain background task.
        service = ImagiAgentService(model=model, agent_kind='initial_build')

        prompt = build_initial_prompt(
            project.name,
            project.description,
            getattr(project, 'design_preferences', ''),
        )

        lead = _ensure_lead_conversation(service, user, project_id, model)
        task = _create_build_task(user, lead, project_id, model, prompt)
        _open_lead_thread(service, lead, prompt, task)

        applied = _build_and_apply(service, task, user, project_id, prompt, builder)

        if applied:
            Project.objects.filter(pk=project_id).update(
                generation_status='completed',
                last_generated_at=timezone.now(),
            )
            logger.info("Initial AI build completed and applied for project %s", project_id)
        else:
            # The project still holds its complete, working scaffold — the
            # unmerged build sits in the workspace for the user to look at.
            Project.objects.filter(pk=project_id).update(generation_status='failed')
            logger.error(
                "Initial AI build for project %s was not applied; project kept its scaffold",
                project_id,
            )
    except Exception:
        logger.exception("Initial AI build crashed for project %s", project_id)
        try:
            Project.objects.filter(pk=project_id).update(generation_status='failed')
        except Exception:
            pass
    finally:
        close_old_connections()


def _apply_despite_lost_auth_links(service, task, user, project_id, auth_problems) -> bool:
    """Merge a build whose only remaining defect is a lost link to auth.

    The auth-link gate blocks the automatic merge for one reason: to buy a
    repair run while the worktree still exists. It is not a verdict on the
    build. Once the repairs are spent, a home page tailored to the founder's
    business but missing its 'Sign in' link is plainly worth more to them than
    the untouched scaffold, and getting the link back is one sentence to their
    main thread. The blocking checks have already passed by the time this
    runs, so what merges here is a page that loads.

    Returns whether the merge landed; a refusal leaves the project on its
    scaffold exactly as before.
    """
    from apps.Imagi.Build.api.views import (
        _apply_task_worktree,
        _conversation_project,
    )

    # The merge rewrites the canonical tree, so it must not race a chat or lead
    # run editing it — the same guard the automatic path applies.
    if service._project_has_live_canonical_run(user, project_id):
        logger.warning(
            "Not applying the initial build for project %s: another run holds "
            "the canonical tree",
            project_id,
        )
        return False

    project = _conversation_project(task)
    if project is None:
        return False

    outcome = _apply_task_worktree(task, project)
    if not outcome.get('ok'):
        logger.error(
            "Could not apply the initial build for project %s: %s",
            project_id,
            outcome.get('detail') or outcome.get('error'),
        )
        return False

    logger.warning(
        "Applied the initial build for project %s even though its home page no "
        "longer links to %s — a tailored page beats the scaffold, and the links "
        "are one request away",
        project_id,
        " or ".join(p['path'] for p in auth_problems),
    )
    return True


def _build_and_apply(service, task, user, project_id, prompt, builder):
    """Run the build, repairing what stands between it and the project.

    Each run ends in the usual task finalization, which merges the worktree
    only when its frontend actually resolves, its app routers still export
    their routes, and its home page still reaches the prebuilt auth pages. So
    "was it applied?" is read back off the conversation, and anything left
    unmerged gets a targeted repair run. Returns whether the work landed in
    the project.

    The three defects are not weighted the same when the repairs run out. A
    dangling import or a broken router means an app that does not load, so
    that build is abandoned and the project keeps its scaffold. A missing auth
    link only means a page that loads and is harder to sign into, so that one
    ships anyway.

    The founder's wait is the binding constraint, so every run in this loop
    shares ONE deadline rather than getting a fresh budget: a build plus its
    repairs is held to INITIAL_BUILD_TIME_BUDGET_S in total. When too little
    time is left for a repair to plausibly finish, it is skipped — starting one
    that gets killed mid-edit tends to leave more dangling references than it
    fixes.
    """
    from apps.Imagi.Build.services.frontend_integrity import (
        find_auth_link_problems,
        find_router_contract_problems,
        find_unresolved_imports,
    )

    attempts = builder.get('INITIAL_BUILD_REPAIR_ATTEMPTS', 2)
    time_budget = builder.get('INITIAL_BUILD_TIME_BUDGET_S', 60)
    min_repair_seconds = builder.get('INITIAL_BUILD_MIN_REPAIR_SECONDS', 12)
    deadline_at = time.monotonic() + time_budget if time_budget else None

    user_input = prompt
    max_turns = builder.get('INITIAL_BUILD_MAX_TURNS')
    cost_budget = builder.get('INITIAL_BUILD_COST_BUDGET_USD')

    for attempt in range(attempts + 1):
        result = service.process(
            user_input=user_input,
            user=user,
            project_id=project_id,
            conversation_id=task.id,
            max_turns=max_turns,
            cost_budget_usd=cost_budget,
            deadline_at=deadline_at,
        )
        if not result.get('success'):
            logger.error(
                "Initial AI build run failed for project %s: %s",
                project_id,
                result.get('error'),
            )
            return False

        task.refresh_from_db()
        if task.review_status == 'accepted':
            return True

        # Not applied. A dangling reference, a broken app-router contract, or a
        # home page that lost its way into the auth pages are the causes worth
        # another run; anything else (a merge conflict, a git failure) needs
        # the user.
        problems = find_unresolved_imports(task.worktree_path)
        router_problems = find_router_contract_problems(task.worktree_path)
        auth_problems = find_auth_link_problems(task.worktree_path)
        found = len(problems) + len(router_problems) + len(auth_problems)
        if not found:
            logger.error(
                "Initial AI build for project %s finished but could not be applied "
                "(review status %r)",
                project_id,
                task.review_status,
            )
            return False

        remaining = deadline_at - time.monotonic() if deadline_at else None
        out_of_attempts = attempt >= attempts
        out_of_time = remaining is not None and remaining < min_repair_seconds
        if out_of_attempts or out_of_time:
            # Only the blocking defects are worth losing the build over.
            if auth_problems and not problems and not router_problems:
                return _apply_despite_lost_auth_links(
                    service, task, user, project_id, auth_problems
                )
            if out_of_attempts:
                logger.error(
                    "Initial AI build for project %s still has %d unresolved "
                    "import(s) and %d router problem(s) after %d repair attempt(s)",
                    project_id,
                    len(problems),
                    len(router_problems),
                    attempts,
                )
            else:
                logger.warning(
                    "Initial AI build for project %s left %d problem(s) with only "
                    "%.1fs of its time budget left; skipping repair so the project "
                    "keeps its working scaffold",
                    project_id,
                    found,
                    remaining,
                )
            return False

        logger.warning(
            "Initial AI build for project %s left %d unresolved import(s), %d "
            "router problem(s) and %d lost auth link(s); starting repair run "
            "%d/%d with %s of time budget left",
            project_id,
            len(problems),
            len(router_problems),
            len(auth_problems),
            attempt + 1,
            attempts,
            f"{remaining:.1f}s" if remaining is not None else "no limit",
        )
        user_input = build_repair_prompt(problems, router_problems, auth_problems)
        max_turns = builder.get('INITIAL_BUILD_REPAIR_MAX_TURNS')
        cost_budget = builder.get('INITIAL_BUILD_REPAIR_COST_BUDGET_USD')

    return False
