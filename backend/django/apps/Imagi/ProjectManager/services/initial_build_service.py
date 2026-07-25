"""
Initial AI build service.

When a user creates a project (their business), the name, description and any
style preferences they provided become the first build prompt for the coding
agent. The build runs in a background thread so project creation stays
fast; by the time the user enters build mode the workspace already has a
tailored starting point instead of the generic scaffold.

It runs the same way every other piece of building work does: the project's
main thread (the 'lead' conversation) opens with the founder's brief and
dispatches it to background subagents ('task' conversations). That gives
the first build the machinery every task already has — each builds in its own
git worktree, so the project the preview serves is never half-written, and
each result is merged in one step when it is finished and sound.

The build is bounded by wall-clock time, not by how much it manages to build:
the founder is waiting on it, so the whole thing — first runs plus any repair
runs — shares one deadline (IMAGI_BUILDER['INITIAL_BUILD_TIME_BUDGET_S'], sized
so the founder waits about half a minute) and ships whatever is finished and
sound when that runs out. This degrades safely because the project already
holds a working scaffold the moment it is created: a build that runs short
means less tailoring, never a broken app.

That deadline is why the pages are built in PARALLEL rather than one after
another. Half a minute is one good write, so a sequential build could only ever
produce a single page. Dispatching one subagent per page instead spends the same
half minute on all of them at once: wall-clock cost is the slowest page, not the
sum. What it does cost is money — three pages is three concurrent agent runs, so
roughly three times the tokens of a single-page build.

Each subagent owns exactly one file (PAGE_BRIEFS below), which is what makes
the parallelism safe on both ends. A self-contained file cannot reference a
component its author never got around to writing, so a run stopped by the clock
still merges; and because no two agents write the same path, the three worktree
merges never conflict. Everything else a web app needs — the Vue and Django
scaffolding, the auth app, and each page's route — is already on disk before
this runs, so no agent has to create the file that would make its own page
reachable.

"Sound" is enforced, not hoped for: a build cut short by a cap can leave a page
importing a component it never wrote, and Vite serves that as a "Failed to
resolve import" error instead of the app. Before a worktree is merged, the
frontend's import graph is checked; a page with dangling references gets a
follow-up repair run from whatever time is left, and one that still doesn't
resolve is never merged — that page keeps its clean, working scaffold while its
siblings ship.

A third check asks whether the home page still links to the sign-in and
register pages, since a wholesale rewrite can quietly drop them and leave auth
nothing points at. That one earns a repair run but never costs the build: a page
that loads and is hard to sign into still beats the scaffold, so an unrepaired
one is merged anyway.

Build progress is tracked on the existing Project.generation_status field
('generating' -> 'completed'/'failed'). Because each page stands alone, this is
not all-or-nothing: the build counts as completed when at least one page landed,
and every page that did not simply keeps its placeholder.
"""

import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.db import close_old_connections
from django.utils import timezone

logger = logging.getLogger(__name__)

# Shown in the workspace as the subagents' thread names.
TASK_TITLE = 'Initial build'


class PageBrief:
    """One page of the first build: who writes what, and what it should be.

    ``requirements`` is the page-specific half of the brief; the shared half
    (the clock, the one-file rule, the design direction, the hard rules) lives
    in coding_agent.INITIAL_BUILD_INSTRUCTIONS, which every page subagent runs
    on.
    """

    def __init__(self, slug, title, view_path, route, summary, requirements):
        self.slug = slug
        self.title = title
        self.view_path = view_path
        self.route = route
        self.summary = summary
        self.requirements = requirements

    @property
    def task_title(self):
        return f'{TASK_TITLE} — {self.slug} page'


# The three pages of a first build, each dispatched to its own subagent. Their
# routes and placeholder views are scaffolded at project creation
# (Build.services.codegen.prebuilt_apps), so every one of these files already
# exists and is already routed before any agent starts.
PAGE_BRIEFS = (
    PageBrief(
        slug='home',
        title='Home page',
        view_path='frontend/vuejs/src/apps/home/views/HomeView.vue',
        route='/',
        summary='the landing page — the first thing anyone sees',
        requirements="""Build a whole landing page: a header carrying the business's name, a hero that says plainly what this business does and for whom, three or four well-differentiated sections (what it offers, how it works, proof or testimonials, FAQ — whatever this business actually needs), a closing call to action, and a footer.

This page also carries the authentication wiring, which the other pages do not. The sign-in and register pages are prebuilt and already working at '/auth/signin' and '/auth/register':
- Keep the scaffold's script setup as it stands: `import { useAuthStore } from '../../auth/stores/index'` and `const authStore = useAuthStore()`. That is the only import your page needs.
- In the header, show the signed-in user when `authStore.isAuthenticated` (their username and a sign-out button calling `authStore.logout($router)`), and when signed out show a 'Sign in' link to '/auth/signin' plus a prominent create-account link to '/auth/register'.
- Make the hero's primary call to action a <router-link> to '/auth/register', worded for this business ("Start your free trial", "Book a table", "Get a quote") rather than a generic "Create account".
- Keep those two paths exact. Do NOT open, restyle, or modify anything under 'frontend/vuejs/src/apps/auth/' — those pages and their backend are prebuilt and secure.""",
    ),
    PageBrief(
        slug='about',
        title='About page',
        view_path='frontend/vuejs/src/apps/about/views/AboutView.vue',
        route='/about',
        summary='the about page — who is behind this business and why it exists',
        requirements="""Build a whole about page: a header, an opening that states what the business stands for, then the sections an about page earns its place with — the story of why it exists, what it believes or how it works, the people or the craft behind it, and a few concrete numbers or milestones if they fit the business. Close with a call to action pointing at the contact page ('/contact') and a footer.

Write it as this specific business would: concrete and grounded, not "we are passionate about excellence". Do NOT add the auth header or the sign-in/register calls to action — the home page owns those. Do not import the auth store.""",
    ),
    PageBrief(
        slug='contact',
        title='Contact page',
        view_path='frontend/vuejs/src/apps/contact/views/ContactView.vue',
        route='/contact',
        summary='the contact page — how a customer reaches this business',
        requirements="""Build a whole contact page: a header, a short line on what to get in touch about, a contact form (name, email, message, and any field this business actually needs — laid out and styled properly), and the other ways to reach the business alongside it (email address, phone, location or hours) as fits.

The form must be presentational only: bind it to local `ref`s and, on submit, show an inline "thanks, we'll be in touch" confirmation in the page. Do NOT post it anywhere — there is no backend endpoint for it and you must not add one. Keep all of it, `ref` imports included, inside your one file.

Do NOT add the auth header or the sign-in/register calls to action — the home page owns those. Do not import the auth store.""",
    ),
)


def _lead_ack(pages) -> str:
    """The lead thread's acknowledgement of the dispatch it just made.

    Written directly rather than generated: the lead's only job here is to hand
    the briefs over, and a model call to produce one fixed sentence would add
    latency and cost to project creation.
    """
    names = ', '.join(p.slug for p in pages)
    if len(pages) == 1:
        return (
            "On it — I've kicked off a subagent to build the first version of "
            "your app. You can watch it work in its thread; I'll let you know "
            "when it's done."
        )
    return (
        f"On it — I've kicked off {len(pages)} subagents to build the first "
        f"version of your app, one per page ({names}), all working at the same "
        "time. You can watch them in their threads; I'll let you know when "
        "they're done."
    )


def build_initial_prompt(
    name: str,
    description: str,
    design_preferences: str = "",
    page: PageBrief = None,
) -> str:
    """Compose one page subagent's brief from the founder's inputs.

    Kept intentionally short: the framing, the freedom to build whatever the
    business needs, the design direction, and the guardrails (keep auth, no
    payments) all live in the initial-build system prompt
    (coding_agent.INITIAL_BUILD_INSTRUCTIONS), which every page shares. This
    message hands over the business being built and the one page this subagent
    owns.

    ``page`` defaults to the home page, which is also what the founder sees as
    the opening message of their main thread.
    """
    page = page or PAGE_BRIEFS[0]

    prompt = f"""This is the first build of a brand-new project — build the first version of this business's web app.

Business name: {name}

Business description (written by the founder):
{description}"""

    design = (design_preferences or "").strip()
    if design:
        prompt += f"\n\nDesign & style preferences (from the founder):\n{design}"

    prompt += f"""

Your page: {page.summary}.
Rewrite '{page.view_path}' (routed at '{page.route}'), and no other file. Your siblings are building the other pages at the same time.

{page.requirements}

When you're done, briefly summarize what you built."""
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


def _open_lead_thread(service, lead, prompt, tasks):
    """Record the dispatch in the main thread, the way a real one reads.

    The founder's brief becomes the opening user message and the lead's
    acknowledgement carries a reference to every subagent thread it started, so
    the transcript and its "watch the subagent" links match every later
    dispatch.
    """
    from apps.Imagi.Build.services.base_agent import (
        build_message_metadata,
        dispatch_task_refs,
    )

    service.add_user_message(lead, prompt)
    service.add_assistant_message(
        lead,
        _lead_ack([t.page for t in tasks]),
        build_message_metadata(
            dispatched_tasks=dispatch_task_refs(
                [{'conversation_id': t.id, 'title': t.title} for t in tasks]
            )
        ),
    )


def _create_build_task(user, lead, project_id, model, prompt, page):
    """Create the subagent conversation one page of the first build runs in.

    An ordinary kind='task' child of the lead: it gets a git worktree of its
    own, auto-applies when it finishes cleanly, and reports back through the
    lead's check-in queue — all of it existing machinery. Siblings differ only
    in their title and the page brief they were queued with.
    """
    from apps.Imagi.Build.models import AgentConversation, SystemPrompt
    from apps.Imagi.Build.services.coding_agent import INITIAL_BUILD_INSTRUCTIONS

    task = AgentConversation.objects.create(
        user=user,
        model_name=model,
        project_id=project_id,
        mode='agent',
        title=page.task_title,
        kind='task',
        parent=lead,
        review_status='active',
        queued_prompt=prompt,
    )
    SystemPrompt.objects.create(
        conversation=task, content=INITIAL_BUILD_INSTRUCTIONS
    )
    # Carried in memory only, so the runner knows which page this task owns
    # without re-deriving it from the title.
    task.page = page
    return task


def _run_one_page(page, task, user_id, project_id, prompt, builder, deadline_at) -> bool:
    """Worker body: build one page and land it, on its own thread.

    Gets its own agent service and its own database connection — neither is
    safe to share across threads — and returns whether this page's work reached
    the project. Never raises: one page failing must not take its siblings
    down with it.
    """
    close_old_connections()
    try:
        from django.contrib.auth import get_user_model
        from apps.Imagi.Build.services.base_agent import ImagiAgentService

        user = get_user_model().objects.get(pk=user_id)
        model = builder.get('INITIAL_BUILD_MODEL') or builder.get('DEFAULT_MODEL')
        service = ImagiAgentService(model=model, agent_kind='initial_build')
        return _build_and_apply(
            service, task, user, project_id, prompt, builder, deadline_at
        )
    except Exception:
        logger.exception(
            "Initial AI build of the %s page crashed for project %s",
            page.slug,
            project_id,
        )
        return False
    finally:
        close_old_connections()


def _run_initial_build(project_id: int, user_id: int) -> None:
    """Thread body: dispatch every page of the first build, then land the results.

    The pages run concurrently against ONE shared deadline, so the founder waits
    for the slowest page rather than the sum of all of them. Each page merges
    itself as it finishes (the merge takes an exclusive lock on the project's
    git repo, so simultaneous finishes serialize safely).
    """
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

        pages = _pages_to_build(builder)
        prompts = {
            page.slug: build_initial_prompt(
                project.name,
                project.description,
                getattr(project, 'design_preferences', ''),
                page,
            )
            for page in pages
        }

        lead = _ensure_lead_conversation(service, user, project_id, model)
        tasks = [
            _create_build_task(
                user, lead, project_id, model, prompts[page.slug], page
            )
            for page in pages
        ]
        # The home page's brief opens the main thread: it is the page the
        # founder is really waiting on, and the whole business description is
        # in it.
        _open_lead_thread(service, lead, prompts[pages[0].slug], tasks)

        # One deadline for everything, started before the first agent does.
        time_budget = builder.get('INITIAL_BUILD_TIME_BUDGET_S', 60)
        deadline_at = time.monotonic() + time_budget if time_budget else None

        with ThreadPoolExecutor(
            max_workers=len(tasks), thread_name_prefix=f'initial-build-{project_id}'
        ) as pool:
            futures = {
                task.page.slug: pool.submit(
                    _run_one_page,
                    task.page,
                    task,
                    user_id,
                    project_id,
                    prompts[task.page.slug],
                    builder,
                    deadline_at,
                )
                for task in tasks
            }
            applied = {slug: future.result() for slug, future in futures.items()}

        _resync_project_files(project_id)

        landed = [slug for slug, ok in applied.items() if ok]
        missed = [slug for slug, ok in applied.items() if not ok]

        if landed:
            Project.objects.filter(pk=project_id).update(
                generation_status='completed',
                last_generated_at=timezone.now(),
            )
            logger.info(
                "Initial AI build completed for project %s: applied %s%s",
                project_id,
                ', '.join(landed),
                f"; {', '.join(missed)} kept their scaffold" if missed else '',
            )
        else:
            # The project still holds its complete, working scaffold — the
            # unmerged builds sit in the workspace for the user to look at.
            Project.objects.filter(pk=project_id).update(generation_status='failed')
            logger.error(
                "No page of the initial AI build for project %s was applied; "
                "project kept its scaffold",
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


def _pages_to_build(builder):
    """The pages this build covers, narrowed by settings if configured.

    IMAGI_BUILDER['INITIAL_BUILD_PAGES'] takes a list of slugs; an unset or
    empty value builds all of them. Unknown slugs are ignored rather than
    failing the build, and an empty result falls back to the home page — the
    first build should never end up dispatching nothing.
    """
    wanted = builder.get('INITIAL_BUILD_PAGES')
    if not wanted:
        return list(PAGE_BRIEFS)
    by_slug = {p.slug: p for p in PAGE_BRIEFS}
    unknown = [slug for slug in wanted if slug not in by_slug]
    if unknown:
        logger.warning(
            "Ignoring unknown INITIAL_BUILD_PAGES entries: %s", ', '.join(unknown)
        )
    pages = [by_slug[slug] for slug in wanted if slug in by_slug]
    return pages or [PAGE_BRIEFS[0]]


def _resync_project_files(project_id: int) -> None:
    """Settle the database mirror once every page has merged.

    Each merge re-syncs the mirror itself, but those syncs run concurrently
    here: a sync that walked disk before a sibling's merge landed can prune the
    rows that sibling just wrote. Disk is the source of truth and is correct
    either way, so rather than serialize the merges, the mirror is simply
    rebuilt once at the end, when nothing else is writing. Best-effort — a
    stale mirror is a debugging inconvenience, not a broken project.
    """
    from ..models import Project

    try:
        from apps.Imagi.Build.services.project_files_service import (
            import_project_from_disk,
        )

        project = Project.objects.get(pk=project_id)
        if project.project_path:
            import_project_from_disk(project)
    except Exception as e:
        logger.warning(
            "Could not re-sync the file mirror for project %s after the initial "
            "build: %s",
            project_id,
            e,
        )


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


def _build_and_apply(service, task, user, project_id, prompt, builder, deadline_at=None):
    """Run one page's build, repairing what stands between it and the project.

    Each run ends in the usual task finalization, which merges the worktree
    only when its frontend actually resolves, its app routers still export
    their routes, and its home page still reaches the prebuilt auth pages. So
    "was it applied?" is read back off the conversation, and anything left
    unmerged gets a targeted repair run. Returns whether the work landed in
    the project.

    The three defects are not weighted the same when the repairs run out. A
    dangling import or a broken router means a page that does not load, so
    that page is abandoned and keeps its scaffold. A missing auth link only
    means a page that loads and is harder to sign into, so that one ships
    anyway.

    The founder's wait is the binding constraint, so every run here shares ONE
    deadline rather than getting a fresh budget — and when the pages are built
    in parallel that deadline is shared across all of them too, passed in by
    the caller so the clock starts once for the whole build rather than per
    page. A build plus its repairs is held to INITIAL_BUILD_TIME_BUDGET_S in
    total. When too little time is left for a repair to plausibly finish, it is
    skipped — starting one that gets killed mid-edit tends to leave more
    dangling references than it fixes.
    """
    from apps.Imagi.Build.services.frontend_integrity import (
        find_auth_link_problems,
        find_router_contract_problems,
        find_unresolved_imports,
    )

    attempts = builder.get('INITIAL_BUILD_REPAIR_ATTEMPTS', 2)
    min_repair_seconds = builder.get('INITIAL_BUILD_MIN_REPAIR_SECONDS', 12)
    if deadline_at is None:
        time_budget = builder.get('INITIAL_BUILD_TIME_BUDGET_S', 60)
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
