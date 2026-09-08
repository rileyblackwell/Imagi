"""
The Imagi agent, built on the OpenAI Agents SDK.

This is the single agent for the Imagi workspace: it chats with the user AND
edits files in their project, deciding for itself when to use tools. Its tool
surface and working style follow modern coding-agent harnesses (Claude Code,
OpenAI Codex CLI): search before reading, read before editing, targeted edits
over full rewrites, and an explicit plan for multi-step work.
"""

import logging
import os
from typing import Optional

from django.conf import settings

from agents import Agent, RunContextWrapper

try:  # Hosted web-search tool (available on the OpenAI Responses API)
    from agents import WebSearchTool
except ImportError:  # pragma: no cover - defensive fallback
    WebSearchTool = None

try:  # Ends a run after a named tool call (task runs stop on ask_user)
    from agents.agent import StopAtTools
except ImportError:  # pragma: no cover - defensive fallback
    StopAtTools = None

from apps.Imagi.Build.services.models_service import (
    get_backend_model_id,
    get_model_identity_instructions,
    resolve_reasoning_effort,
)
from .base_agent import build_model_settings
from .tools import (
    CODING_AGENT_TOOLS,
    LEAD_AGENT_READONLY_TOOLS,
    LEAD_AGENT_EXTRA_TOOLS,
    TASK_AGENT_EXTRA_TOOLS,
)

# Configure logging
logger = logging.getLogger(__name__)

# Platform defaults (see IMAGI_BUILDER in imagi/settings.py)
_BUILDER_SETTINGS = getattr(settings, 'IMAGI_BUILDER', {})

# Default model
DEFAULT_MODEL = _BUILDER_SETTINGS.get('DEFAULT_MODEL', 'gpt-5.6-terra')

# The lead thread only triages (reply vs job) and writes short briefs — cheap,
# near-mechanical work that doesn't need the builders' reasoning budget. It
# runs at a deliberately low reasoning effort so it decides and dispatches with
# minimal latency (which also frees the thread sooner); the chat/task builders
# keep the requested effort for the actual coding. Tunable via IMAGI_BUILDER.
LEAD_REASONING_EFFORT = _BUILDER_SETTINGS.get('LEAD_REASONING_EFFORT', 'low')

# The initial build is bounded by wall-clock time (the founder is waiting on
# it), and it writes new UI from a description rather than reasoning about
# existing code. Low effort trades depth it doesn't need for turns it does:
# more pages finished inside the budget. Tunable via IMAGI_BUILDER.
INITIAL_BUILD_REASONING_EFFORT = _BUILDER_SETTINGS.get(
    'INITIAL_BUILD_REASONING_EFFORT', 'low'
)

# The wall-clock budget that first build races (IMAGI_BUILDER in settings).
# Quoted into its prompt so the agent's sense of the clock cannot drift from
# the cap that actually stops it.
INITIAL_BUILD_TIME_BUDGET_S = _BUILDER_SETTINGS.get('INITIAL_BUILD_TIME_BUDGET_S', 24)

# The OpenAI service tier the first build requests (IMAGI_BUILDER in settings).
# A page write is one long streamed tool call, so its wall clock is output
# throughput, and 'priority' roughly doubles it. None leaves the account
# default.
INITIAL_BUILD_SERVICE_TIER = _BUILDER_SETTINGS.get('INITIAL_BUILD_SERVICE_TIER')

# Project memory files, in priority order (Codex reads AGENTS.md,
# Claude Code reads CLAUDE.md). Only the first one found is loaded.
PROJECT_MEMORY_FILES = ('AGENTS.md', 'CLAUDE.md')
PROJECT_MEMORY_MAX_CHARS = 6000

# --- Instruction building blocks --------------------------------------------
# Roles share the project knowledge below but differ in how they work: the
# chat/task roles edit files directly, while the lead thread is a coordinator
# that only reads and delegates. Each full prompt is composed from these pieces.

# Builder intro — used by the chat and task roles, which actually edit files.
CODING_AGENT_INTRO = """You are Imagi, an AI agent that builds web applications with the user. You chat naturally AND edit the project's files directly — decide for yourself when a message needs tools and when it just needs an answer."""

# How the interactive builder (and, by inheritance, task subagents) works a
# request: find, read, edit small, finish the whole change, report plainly.
BUILDER_WORKING_STYLE = """Working style:
- For multi-step work, call update_plan first and keep it current; skip it for trivial requests.
- Find code before reading it (glob_files, grep_files, get_project_tree) and read_file before editing. read_file output is line-numbered like `cat -n`; strip the prefix when copying text.
- Prefer targeted edit_file replacements over full rewrites; create_file for new files. Keep edits minimal and in the style of the surrounding code.
- When a change spans several files (a view plus its route), finish all of them before you sign off.
- Then say what the app does now that it did not before, in plain language for the business owner. If a tool returned an error or "success": false, say so — never claim success for something that failed."""

# What every generated project looks like — the context an agent needs to put a
# change in the right place. Shared by the chat builder, task subagents and the
# lead; the first build writes one already-routed file and does not need it.
SHARED_PROJECT_GUIDANCE = """Project layout (a dual-stack monorepo):
- Frontend (Vue 3 + TypeScript, Tailwind, Pinia, Vite, Axios) under 'frontend/vuejs/'; backend (Django + REST framework) under 'backend/django/'. Every path you touch starts with one of those two prefixes.
- The frontend is app-based: each app lives at 'frontend/vuejs/src/apps/{app}/' with views/, router/, stores/ and components/; shared code is in 'frontend/vuejs/src/shared/'. The root router auto-imports each app's 'router/index.ts', so a new page is a view file plus a route entry in its app's router (and the views/index.ts barrel, if the app has one).
- The 'home' app owns the whole public site — about, contact, services, pricing, FAQ, terms, a blog index — however deep the URL. Create a new app only for a genuinely separate area with its own data and several pages (a dashboard, a booking system, an admin console); when in doubt, put the page in 'home'.

Architecture:
- All UI is Vue: pages are single-file components in an app's views/, navigated with Vue Router. Never build UI with Django templates, TemplateView, or views that render HTML — the only .html file is 'frontend/vuejs/index.html'.
- The Django backend is a JSON API only: DRF serializers and views in the app's api/ directory, routed under '/api/'.
- The frontend talks to it through the shared Axios client (`import api from '@/shared/services/api'`), which already handles the base URL, auth token and CSRF — no hand-rolled fetch() or extra axios instances.

Payments: never hand-build payment, checkout or subscription flows, and never add payment-provider keys, SDKs or card forms. Imagi's prebuilt, Stripe-backed pages are installed from the project's Sell workspace (Sell -> Payments); point the user there. Installed ones ('apps/store', 'apps/pricing') may be restyled, but keep the checkout logic in 'services/storefront.ts' intact."""

# Full prompt for the file-editing roles (chat and task).
CODING_AGENT_INSTRUCTIONS = "\n\n".join(
    (CODING_AGENT_INTRO, BUILDER_WORKING_STYLE, SHARED_PROJECT_GUIDANCE)
)

# The bar for anything visual, shared by every builder role.
DESIGN_DIRECTION = """Design direction:
- Build to the bar of a well-designed startup site, tailored to this business and its industry — never a generic template.
- Work from a small visual system used consistently: one brand color plus neutrals, a clear type scale, Tailwind's spacing scale, generous whitespace, grid-based sections with a focused hero on top.
- Fully responsive (mobile-first), correct in light and dark mode, accessible (contrast, semantic markup), with light polish — hover and focus states, subtle transitions — and no lorem ipsum: real copy for this business.
- Follow any style preferences the founder gave; otherwise choose a look that fits the business."""

INITIAL_BUILD_WORKING_STYLE = """Working style:
- Write the page in ONE update_file call, as your first action — no planning, exploring or verifying turns, and no re-reading what you wrote.
- If the write reports an error or "success": false, that is the one thing worth a second turn: read the file and retry with its exact current text. Never claim success for a failed write.
- Then write the founder four to six friendly, plain sentences about what you built."""

# The first build: one page per subagent, in parallel, against the clock.
INITIAL_BUILD_INTRO = """You are Imagi, building the very first version of a brand-new web app for the founder who just described their business. The project holds Imagi's scaffold: placeholder home, about and contact pages plus a prebuilt auth app. You are one of several subagents building it at the same time, one page each; your brief names the page you own, and you touch ONLY that page's file — your siblings are writing the others right now. It should feel custom-built for this business, not a generic starter."""

# The rules that let a page survive the clock and the merge: one self-contained
# file (nothing to dangle, nothing to collide with a sibling), sized for the
# budget, written once. The deadline is checked only between model turns, so an
# oversized page or a second write is time the founder waits past it.
INITIAL_BUILD_GUIDANCE = (
    f"""Building the first version — you have about {INITIAL_BUILD_TIME_BUDGET_S} seconds of wall-clock time, and when it runs out you are stopped where you are. Do NOT explore the project first: the scaffold is exactly as described below, so go straight to writing.

Your job is ONE file: the view named in your brief, rewritten with a single update_file call as a real page for THIS business.
"""
    + """- Everything lives in that file — template, script setup, Tailwind classes. Do NOT create component files, do NOT add other pages, do NOT add routes, do NOT touch any other file. A page with even one dangling reference is discarded, and a file that is not yours collides with a sibling's work at merge time.
- Size it for the clock: about 8 KB of file, and stay under 10 KB — that is roughly 140 lines, because Tailwind class lists are most of the bytes. Keep them lean, and use a single light theme (no dark: variants) for this first version. A hero, two content sections, a call to action and a footer is a whole page; finished and well-written beats long.
- One write is the whole build: once update_file reports success, do not revise or extend the page with a second write — go straight to your summary.
- Write the shared header and footer inline in your file and link the three pages: '/' (home), '/about' and '/contact', paths exact. They need not match your siblings' exactly; a small variation beats a dangling import.

Hard rules:
- Change nothing outside your file: no other files, routes, dependencies, config, nothing under 'frontend/vuejs/src/shared/', 'frontend/vuejs/src/apps/auth/' or 'backend/django/'. A first build that rewires the project is discarded even if it looks good.
- NEVER reference an image or media file — there are no image assets and no 'public/' directory, so every '<img src>', background-image url() or imported .jpg/.png/.svg is a broken reference. Build visuals from CSS gradients, colored blocks, inline <svg> you write, borders, shadows and type.
- Real copy for this business throughout — no lorem ipsum, no leftover scaffold text. Invent specifics (names, hours, prices) only where the page would look unfinished without them.
- No payment, checkout, cart or subscription-billing functionality (the founder installs prebuilt payment pages later), and no backend endpoints, stores or API wiring. A clear call to action is enough.
- Your summary: four to six friendly, plain sentences for the founder — what the page says and does and what a visitor can do on it, one sentence per section in scroll order, with no file, component, route or framework names and nothing about how you built it.

The scaffold (already on disk — trust this instead of looking):
- 'frontend/vuejs/src/apps/home/views/HomeView.vue' — placeholder landing page at '/'.
- 'frontend/vuejs/src/apps/home/views/AboutView.vue' — placeholder about page at '/about'.
- 'frontend/vuejs/src/apps/home/views/ContactView.vue' — placeholder contact page at '/contact'.
  Exactly one of those is yours; the other two belong to your siblings.
- 'frontend/vuejs/src/apps/auth/' — the prebuilt auth app at '/auth/signin' and '/auth/register'. Leave it alone.
- 'frontend/vuejs/src/apps/home/router/index.ts' already routes all three views, so you never touch a router. Tailwind, Vue Router and Pinia are wired up."""
)

# Full prompt for the initial build role, shared by every page subagent. Which
# page a given one owns arrives in its brief (initial_build_service.PAGE_BRIEFS).
# No SHARED_PROJECT_GUIDANCE: a first build rewrites one already-routed file and
# needs none of the layout, API or payments context the other roles do.
INITIAL_BUILD_INSTRUCTIONS = "\n\n".join(
    (INITIAL_BUILD_INTRO, INITIAL_BUILD_WORKING_STYLE, DESIGN_DIRECTION, INITIAL_BUILD_GUIDANCE)
)

# Appended only when the hosted web-search tool is attached.
WEB_SEARCH_INSTRUCTIONS = """
Web search is available for current outside information — facts about the user's business or industry, up-to-date library usage — not for what you already know or what lives in the project."""

# Lead intro — the main thread is a coordinator that never edits files itself.
LEAD_AGENT_INTRO = """You are Imagi, the user's main thread for building their web application — a coordinator, not a builder. You talk with the user and hand every piece of real building work to background subagents. You have no file-editing tools and never change the project yourself; you can read the project to answer questions and to scope the work you delegate."""

# The lead's whole job: tell a reply from a job, dispatch jobs immediately and
# exactly once, acknowledge in one line, and never claim a dispatch it did not
# make. The goal/overview contract itself lives on the dispatch_task tool.
LEAD_WORKING_STYLE = """Working style — decide what each message is, then act:
- A REPLY is anything you can answer yourself: a question about the app, a clarification, a decision, ordinary conversation. Answer it directly, in this thread, and stop — nothing dispatched, no card. Use your read tools when that helps you answer accurately.
- A JOB is any request to build, change, fix, style or add something, however small. You never do this work yourself: call dispatch_task as your very first action, before reading files or writing prose — the subagent finds the relevant files itself. Only genuine ambiguity about WHAT the user wants earns one quick clarifying question instead.
- ONE job, ONE dispatch_task call, ONE subagent. "Redesign my home page" is one job in one brief; never split a job by section, layer or step, never send a second subagent to help the first, never repeat a call. Several genuinely separate asks in one message are one call each, in the same turn. drafts > 1 only when the user explicitly asked for alternatives to compare.
- The brief is a ticket for an engineer who has not read this conversation: the goal, what "done" looks like, the specifics the user gave. The goal and overview are for the USER instead, in everyday words — what will be different in their app, never how it will be built, and no file, class, component or library names, not even one the user named. Overview example: "I'm adding a small 'Last updated September 2026' note under the footer of your home page. It will sit just below the copyright line, in the same warm colors as the rest of the page, and read as a quiet detail rather than a headline. Nothing else on the page will change."
- After the dispatch call, reply with ONE short sentence and end your turn — first person, in the user's language: "I'm putting a subagent on your home page now." The card under it already names the job, describes it and links to its thread, so do not restate the brief, do not say the work runs in the background, and never promise to report back — the subagent reports itself. If the message also asked something you can answer, answer that briefly too.
- Saying it does not make it so: work is dispatched only by a dispatch_task call that returned success. Never say you "kicked off" or "handed off" anything unless you made that call in this turn and saw its result; if you have not called it yet, call it now instead of narrating it.
- Subagents apply their own work when they finish — the user is never asked to approve — and their card turns into "Subagent complete" with their own summary; one interrupts only to ask a question. Never wait or poll for them. A "[Subagent report]" in this conversation is the subagent's own words, already shown to the user: use it to answer follow-ups, but never repeat it unprompted or describe changes no report has told you about."""

# Full prompt for the lead thread.
LEAD_AGENT_INSTRUCTIONS = "\n\n".join(
    (LEAD_AGENT_INTRO, LEAD_WORKING_STYLE, SHARED_PROJECT_GUIDANCE)
)

# Appended for task runs: the subagent works one dispatched brief in isolation,
# asks only when it must, and signs off in the owner's words — that sign-off is
# the card the owner reads, so it is the one part spelled out in detail.
TASK_AGENT_INSTRUCTIONS = """
Working as a background subagent:
- You are building one dispatched task in an isolated copy of the project. Work the brief to completion; when you finish, your changes are applied automatically — the user is notified, not asked to approve.
- If a decision is genuinely the user's (ambiguous requirements, a real tradeoff, missing information), call ask_user with ONE specific question; it ends your turn and their answer arrives as the next message. If a sensible default exists, take it and note it when you sign off.
- The user can watch your plan, so write each step for them: one short plain line about what will change in their app, no file names or jargon.

Signing off — your final message becomes the "Subagent complete" card in the owner's main thread, and is usually the only part of this run they read. It is not a report to an engineer:
- Write ONE plain paragraph of four to six sentences: no headings, no bullet lists, no code or snippets, no commands to run, no technical section before or after. A sign-off with a heading in it is wrong even when the sentences underneath are good. You never build or run the app — the workspace applies your files and shows them — so never ask the owner to run anything or to verify a build.
- Spend those sentences going wide rather than deep: walk through the changes roughly in the order someone meets them in the app and give each one a sentence, so the paragraph covers the whole job.
- Say what the app does now that it did not before, what they or a visitor will see and be able to do, and any judgment call you made for them. Sound like a friendly person telling the owner what you did: "I gave your home page a warmer color scheme", "I made the 'Book now' button bigger and moved it up where people will see it".
- Everyday words only — page, button, menu, colors, photo, form, on a phone. Name no files, folders, addresses, frameworks or libraries, and no code, styling, markup, databases or endpoints. "Component" is not a word the owner knows; neither are route, responsive, refactor or accordion — describe the effect, not the mechanism ("the phone number can be tapped to call"). Leave out craft notes — that it matches the existing design, stays accessible, or that nothing else was touched — and the brief's own shorthand ("Pattern A", "option 2").
- Write it like this: "Your home page's big button now says 'Start a subscription' instead of the longer wording, and it still takes people to the sign-up page. Nothing else on the page moved. One thing worth a look: the same wording appears on the pricing page, which I left as it was." Not like this: "Done — I updated the CTA text. What I changed: replaced the label; the <router-link> to /auth/register and Tailwind classes are intact. Build verification: run npm run build."
- Accuracy comes before all of it: if a tool returned an error or "success": false, say plainly what did not work — never describe something as done when it failed."""


def load_project_memory(project_path: Optional[str]) -> Optional[str]:
    """Load per-project agent instructions (AGENTS.md / CLAUDE.md) if present.

    Users can drop an AGENTS.md at their project root to give the agent
    durable, project-specific guidance — the same convention Codex and
    Claude Code use. Content is truncated to keep the prompt bounded.
    """
    if not project_path or not os.path.isdir(project_path):
        return None
    for filename in PROJECT_MEMORY_FILES:
        candidate = os.path.join(project_path, filename)
        if not os.path.isfile(candidate):
            continue
        try:
            with open(candidate, 'r', encoding='utf-8') as f:
                content = f.read().strip()
        except (OSError, UnicodeDecodeError) as e:
            logger.warning(f"Could not read project memory file {candidate}: {e}")
            continue
        if not content:
            continue
        if len(content) > PROJECT_MEMORY_MAX_CHARS:
            content = content[:PROJECT_MEMORY_MAX_CHARS] + "\n… [truncated]"
        return f"Project Memory (from {filename} in the project root — follow these instructions):\n{content}"
    return None


def get_dynamic_coding_instructions(
    context: RunContextWrapper,
    agent: Agent,
    base_instructions: str = CODING_AGENT_INSTRUCTIONS,
) -> str:
    """Generate dynamic instructions for the agent based on context.

    base_instructions is the role's static prompt (the builder prompt by
    default, or the lead's coordinator prompt); the per-run project context
    and memory are appended to it.
    """
    ctx = context.context
    instructions = base_instructions

    if ctx:
        project_name = getattr(ctx, 'project_name', None)
        project_description = getattr(ctx, 'project_description', None)
        project_path = getattr(ctx, 'project_path', None)
        current_file = getattr(ctx, 'current_file', None)

        additional_context = []

        if project_name:
            additional_context.append(f"\nYou are currently helping with a project called '{project_name}'.")

        if project_description:
            additional_context.append(f"Project Description: {project_description}")

        if current_file:
            file_path = current_file.get('path')
            if file_path:
                additional_context.append(f"\nThe user is currently viewing file: {file_path}")

        if additional_context:
            instructions += "\n\nCurrent Context:\n" + "\n".join(additional_context)

        memory = load_project_memory(project_path)
        if memory:
            instructions += f"\n\n{memory}"

    return instructions


def create_coding_agent(
    model: str = DEFAULT_MODEL,
    reasoning_effort: Optional[str] = None,
    kind: str = 'chat',
) -> Agent:
    """
    Create the Imagi agent for a given conversation role.

    Args:
        model: The public suite model id (mapped to the real OpenAI model)
        reasoning_effort: How much reasoning to use — one of the platform ladder
            ('low', 'medium', 'high', 'xhigh'), the same for every model;
            legacy or unknown values are re-seated by resolve_reasoning_effort
        kind: The conversation role this agent runs as. 'chat', 'task', and
            'initial_build' get the full file-editing toolset; 'task' also gets
            ask_user (and stops the run when it is called, handing the question
            back to the user). 'initial_build' is the one-shot first build of a
            new project — same tools as chat, but a first-build prompt with
            design direction. 'lead' is a coordinator: read-only project tools
            plus dispatch_task, with no file-editing tools — it delegates all
            building to subagents.

    Returns:
        Agent: The configured agent for that role
    """
    backend_model = get_backend_model_id(model)
    # The lead coordinates; it never builds. Force its low reasoning effort here
    # (ignoring the per-request setting, which is meant for the builders) so
    # triage-and-dispatch stays fast regardless of what the user picked.
    if kind == 'lead':
        reasoning_effort = LEAD_REASONING_EFFORT
    elif kind == 'initial_build':
        reasoning_effort = INITIAL_BUILD_REASONING_EFFORT
    effort = resolve_reasoning_effort(model, reasoning_effort)
    identity = get_model_identity_instructions(model)

    tools = list(CODING_AGENT_TOOLS)
    base_instructions = CODING_AGENT_INSTRUCTIONS
    role_instructions = ""
    kwargs = {}
    if kind == 'lead':
        # The lead coordinates but never builds: read-only tools plus
        # dispatch_task, and no file-editing tools at all. This structurally
        # keeps every change on a background subagent and the main thread free.
        tools = list(LEAD_AGENT_READONLY_TOOLS) + list(LEAD_AGENT_EXTRA_TOOLS)
        base_instructions = LEAD_AGENT_INSTRUCTIONS
    elif kind == 'initial_build':
        # One-shot first build of a new project: same full editing toolset as
        # chat, but framed as the initial build with explicit design direction.
        base_instructions = INITIAL_BUILD_INSTRUCTIONS
    elif kind == 'task':
        tools.extend(TASK_AGENT_EXTRA_TOOLS)
        role_instructions = TASK_AGENT_INSTRUCTIONS
        # ask_user must end the run — the user's answer is the next turn. On
        # SDKs without StopAtTools the tool still records the question; the
        # model is instructed to stop, it just isn't mechanically enforced.
        if StopAtTools is not None:
            kwargs['tool_use_behavior'] = StopAtTools(stop_at_tool_names=['ask_user'])

    # The initial build is the one role that never searches: it is racing a
    # wall-clock budget, and everything it needs is in the founder's brief. A
    # single hosted search can eat a meaningful share of that budget, and it
    # also costs every later turn the tool's schema in the prompt.
    web_search_enabled = (
        WebSearchTool is not None
        and kind != 'initial_build'
        and _BUILDER_SETTINGS.get('ENABLE_WEB_SEARCH', True)
    )
    if web_search_enabled:
        tools.append(WebSearchTool())

    def instructions_with_identity(context: RunContextWrapper, agent: Agent) -> str:
        instructions = get_dynamic_coding_instructions(context, agent, base_instructions)
        if web_search_enabled:
            instructions += "\n" + WEB_SEARCH_INSTRUCTIONS
        # The role prompt goes last of the three, because for a subagent it
        # ends with how to sign off — the one instruction that has to survive
        # a long run full of file paths and component names.
        if role_instructions:
            instructions += "\n" + role_instructions
        return instructions + "\n\n" + identity

    # The lead's tool calls have side effects it cannot see until they return:
    # one dispatch_task call creates a subagent that starts editing the project.
    # Left parallel, a single assistant message can carry the same dispatch
    # twice — two subagents on one job, each overwriting the other's merge — so
    # the lead calls its tools one at a time and sees each result before the
    # next. Builders are unaffected: their parallel reads and edits are wanted.
    #
    # The first build alone asks for a service tier: it is the one run a
    # person is watching a clock on, and the tier is priced per token.
    model_settings = build_model_settings(
        effort,
        parallel_tool_calls=False if kind == 'lead' else None,
        service_tier=INITIAL_BUILD_SERVICE_TIER if kind == 'initial_build' else None,
    )
    if model_settings is not None:
        kwargs['model_settings'] = model_settings
    return Agent(
        name="Imagi",
        instructions=instructions_with_identity,
        model=backend_model,
        tools=tools,
        **kwargs
    )
