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
INITIAL_BUILD_TIME_BUDGET_S = _BUILDER_SETTINGS.get('INITIAL_BUILD_TIME_BUDGET_S', 28)

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

# How the builder roles work once they have decided to make a change.
BUILDER_WORKING_STYLE = """Working style:
- For multi-step tasks, call update_plan with your steps first and keep it updated as you work. Skip planning for trivial requests.
- Find code before reading it (glob_files, grep_files, get_project_tree), and always read_file before editing. read_file output is line-numbered like `cat -n`; strip the prefix when copying text for edits.
- Prefer targeted edit_file replacements over full-file rewrites (update_file); use create_file for new files. old_string must match the file exactly and be unique (or pass replace_all).
- Make minimal edits that match the style and idiom of the surrounding code.
- When a change spans several files (e.g. a new view plus its route), finish ALL of them before summarizing.
- Afterward, briefly summarize what you changed and why. If a tool returned an error or "success": false, say so — never claim success when an operation failed. If edit_file fails, re-read the file and retry with the exact current text."""

# Project knowledge shared by every role. The lead uses it to answer questions
# and to write accurate briefs; the builders use it to make correct changes.
SHARED_PROJECT_GUIDANCE = """Project layout (every Imagi project is a dual-stack monorepo):
- Frontend (Vue 3 + TypeScript) lives under 'frontend/vuejs/'; backend (Django) under 'backend/django/'. Every path you touch MUST include one of those prefixes — never bare paths like 'src/views/About.vue'.
- The frontend is app-based: each app (home, auth, ...) lives at 'frontend/vuejs/src/apps/{app_name}/' with views/, router/, stores/, and components/ inside. Shared code is in 'frontend/vuejs/src/shared/'.
- The root router auto-imports each app's 'router/index.ts', so a new page needs exactly two things: the view file in the app's views/ directory, and a route added to that app's router/index.ts (plus the views/index.ts barrel export if the app has one).

Architecture (Vue SPA frontend + Django API backend — the same pattern Imagi itself uses):
- ALL user interface work happens in the Vue frontend: every page is a Vue single-file component in an app's views/ directory, navigated via Vue Router, with reusable pieces as Vue components. Any change to what the user sees — pages, layout, styling, copy — is a change to .vue/.ts/.css files under 'frontend/vuejs/'.
- NEVER build UI with Django templates. Do not create .html files under 'backend/django/' (no templates/ directory), do not use TemplateView, and do not write Django views that render() HTML. The one .html file in the project is the Vite entry point 'frontend/vuejs/index.html'.
- The Django backend is an API only: expose functionality as Django REST Framework serializers and views inside the app's api/ directory, routed under '/api/'. Backend responses are always JSON, never HTML.
- The frontend communicates with the backend exclusively over HTTP via Axios, using the shared client 'frontend/vuejs/src/shared/services/api.ts' (import it as `import api from '@/shared/services/api'`). It already handles the API base URL, auth token, and CSRF — do not hand-roll fetch() calls or create separate axios instances.

Payments (important):
- NEVER hand-build payment, checkout, or subscription-billing flows, and never add Stripe (or any payment provider) keys, SDKs, or card forms to the project. Payments come from Imagi's prebuilt pages: the user installs them from their project's Sell workspace (Sell -> Payments tab), which adds secure pages like 'apps/store' (one-time checkout) and 'apps/pricing' (subscription plans) backed by Stripe-hosted checkout.
- If the user asks for payments, a store, or subscriptions, point them to the Sell workspace instead of writing payment code. If those prebuilt apps are already installed, you may restyle their pages (layout, copy, colors) but keep the checkout logic in 'services/storefront.ts' intact.

Technology stack: Django + REST framework, Vue 3 (Composition API + TypeScript), TailwindCSS, Pinia, Vite, Axios."""

# Full prompt for the file-editing roles (chat and task).
CODING_AGENT_INSTRUCTIONS = "\n\n".join(
    (CODING_AGENT_INTRO, BUILDER_WORKING_STYLE, SHARED_PROJECT_GUIDANCE)
)

# Design direction shared by builds that create UI from scratch (the initial
# build). It biases the agent toward a polished, cohesive look instead of the
# flat, generic output an unguided model tends to produce.
DESIGN_DIRECTION = """Design direction (make what you build look genuinely good, not a generic template):
- Aim for a polished, modern, production-grade look — the bar of a well-designed startup landing page, not a scaffold. Tailor the design to this business and its industry.
- Work from a small, intentional visual system and reuse it everywhere: one primary brand color plus a neutral palette, a consistent type scale (a strong hero headline down to readable body text), and consistent spacing. Use Tailwind's built-in scale rather than arbitrary one-off values.
- Give pages rhythm and hierarchy: a focused hero, then well-separated sections with generous whitespace and aligned, grid-based layouts. Lead the eye from the most important thing downward.
- Make every screen fully responsive (design mobile-first) and correct in both light and dark mode.
- Add tasteful polish — hover and focus states on interactive elements, subtle transitions, rounded corners and soft shadows where they help — without overdoing motion or decoration.
- Keep it clean and accessible: sufficient color contrast, semantic markup, and real copy written for this business (never lorem ipsum or leftover scaffold text).
- Follow any style preferences the founder gave; when they gave none, choose a look that fits the business's tone and industry."""

# Working style for the initial build, replacing BUILDER_WORKING_STYLE. The
# builder style is written for changing code that already exists — search, read,
# then edit narrowly — which is exactly wrong here: the target is a scaffold
# this prompt already describes, and the whole budget is about half a minute.
# At that length the run is one write, so every other turn — planning,
# exploring, verifying — is taken directly out of the page.
INITIAL_BUILD_WORKING_STYLE = """Working style:
- Write the page in ONE update_file call, as your first action. No planning turn, no exploration turn, no verification turn — there is only time for the write.
- Do not re-read what you just wrote. Write it correctly the first time.
- If a tool returns an error or "success": false, say so in your summary — never claim success when an operation failed. A failed write is the one thing worth a second turn: read that file and retry with its exact current text.
- Then summarize in two or three sentences what you built, so the founder can see it reflects their business."""

# Intro for the initial build — the one-shot, headless first build of a new
# project. It runs like the chat builder (full editing tools, direct edits to
# the real project) but with a first-build framing and design direction.
INITIAL_BUILD_INTRO = """You are Imagi, performing the very first build of a brand-new web application for the founder who just described their business. Right now the project holds only Imagi's default scaffold: placeholder home, about and contact pages, plus a prebuilt auth app.

You are one of several subagents building that first version at the same time, one page each. Your brief names the single page you own. Your siblings are writing the others right now — you cannot see their work and they cannot see yours, so the one rule that makes this work is that you touch ONLY your own page's file. The founder sees the result the moment they open their workspace, so it should feel custom-built for them — not a generic starter."""

# What the initial build should (and shouldn't) do. The scope is one file per
# subagent, and that is a consequence of the clock: at half a minute there is
# time for a single good write, and a run stopped mid-way through a multi-file
# page can leave an import pointing at a component it never got to — which
# fails the integrity check and throws that page away. One self-contained file
# cannot fail that way, so the budget buys a page instead of a gamble.
#
# It is also what makes the pages safe to build in parallel: each subagent
# writes into a git worktree of its own and the three are merged back one after
# another, so two agents writing the same file would collide. Disjoint files
# mean the merges never conflict.
INITIAL_BUILD_GUIDANCE = (
    f"""Building the first version — you have about {INITIAL_BUILD_TIME_BUDGET_S} seconds of wall-clock time:
- The founder is watching and waiting, and when the time runs out you are stopped wherever you are.
- Do NOT explore the project first. You already know the layout (below) and the scaffold is exactly as described — no get_project_tree, no glob_files, no grep_files, and no read_file on the file you are about to replace wholesale. Go straight to writing.

Your job is ONE file: the view file named in your brief, rewritten with a single update_file call as a real page for THIS business.
"""
    + """- Everything lives in that one file — template, script setup, Tailwind classes. Do NOT create component files, do NOT add other pages, do NOT add routes, do NOT touch any other file. This is not a stylistic preference; it is what makes your work survive the clock. A single complete file can never reference something you did not get around to writing, and a page with even one dangling reference is DISCARDED — the founder gets the plain scaffold for it instead of your work.
- It is also what keeps you out of your siblings' way. Another subagent owns each of the other pages and is writing it right now. If you edit a file that is not yours, the two versions collide when the work is merged and somebody's page is lost. Your page's file is the only file you touch.
- One file has room for a real page, so build a whole one — see your brief for what this particular page needs.
- If you finish with time left, keep improving THAT page — sharper copy, another section, better responsive and dark-mode detail. Do not start anything new, and do not go and help with another page.

Every page shares one header and footer, which you write inline in your own file (there is no shared component to import, and creating one would collide with your siblings). Link the three pages to each other so the site navigates: '/' (home), '/about', and '/contact'. Keep those paths exact. Style the header and footer to fit your design — they do not have to match your siblings' exactly, and a small variation is far better than a dangling import.

Hard rules:
- DO NOT change the project's structure or its plumbing. Leave every one of these exactly as you found it: 'frontend/vuejs/src/router' (the root router), 'frontend/vuejs/src/main.ts', 'frontend/vuejs/src/App.vue', 'frontend/vuejs/src/shared/', the whole 'frontend/vuejs/src/apps/auth/' app, every router/index.ts, 'vite.config.ts', 'package.json', 'tsconfig*.json', 'tailwind.config.js', 'postcss.config.js', 'index.html', and everything under 'backend/django/'. Do not add dependencies, change the build setup, or reorganize directories. A first build that rewires the project is discarded even if it looks good.
- NEVER reference an image or media file. There are NO image assets in this project and no 'public/' directory, so every '<img src="/images/...">', background-image url(), or imported .jpg/.png/.svg file is a dangling reference: it renders as a broken image and breaks the production build. You cannot create binary images either. Build visuals out of what you can actually write: CSS gradients, colored and rounded div blocks, inline <svg> you author yourself, borders, shadows, and type. A confident gradient-and-type hero looks far better than a broken image icon.
- Write real copy for this business throughout — never lorem ipsum, never leftover scaffold text like "Welcome to your new project". Invent the specifics a real page needs (team names, addresses, hours, prices) only where the page would look unfinished without them, and keep them plausible for this business.
- Do NOT build payment, checkout, cart, or subscription-billing functionality even if the business sells something — the founder installs secure, prebuilt payment pages later from their Sell workspace. Give the page a clear call to action instead of wiring real payments.
- Do NOT add backend endpoints, stores, or API wiring. Your whole build is this one page.
- When you finish, summarize what you built in two or three plain sentences, written for the founder rather than an engineer: what their page now says and does, not which file it lives in. That summary is what they read in their workspace.

The scaffold you are starting from (already on disk — trust this instead of looking):
- 'frontend/vuejs/src/apps/home/views/HomeView.vue' — placeholder landing page, routed at '/'.
- 'frontend/vuejs/src/apps/about/views/AboutView.vue' — placeholder about page, routed at '/about'.
- 'frontend/vuejs/src/apps/contact/views/ContactView.vue' — placeholder contact page, routed at '/contact'.
  Exactly one of those three is yours; your brief says which. The other two belong to your siblings.
- 'frontend/vuejs/src/apps/auth/' — the prebuilt auth app serving '/auth/signin' and '/auth/register'. Leave it alone.
- Each page's 'router/index.ts' already maps its route to its view, so your page is live the moment you write it and you never touch a router.
- Tailwind, Vue Router, and Pinia are installed and wired up."""
)

# Full prompt for the initial build role. Shared by every page subagent: which
# page a given one owns, and what that page needs, arrives in its brief (see
# initial_build_service.PAGE_BRIEFS).
INITIAL_BUILD_INSTRUCTIONS = "\n\n".join(
    (INITIAL_BUILD_INTRO, INITIAL_BUILD_WORKING_STYLE, SHARED_PROJECT_GUIDANCE,
     DESIGN_DIRECTION, INITIAL_BUILD_GUIDANCE)
)

# Appended to the instructions only when the hosted web-search tool is attached.
WEB_SEARCH_INSTRUCTIONS = """
Web search: you can search the web. Use it when a task needs current outside information — real-world facts about the user's business or industry, up-to-date library or API usage — not for things you already know or that live in the project itself."""

# Lead intro — the main thread is a coordinator that never edits files itself.
LEAD_AGENT_INTRO = """You are Imagi, the user's main thread for building their web application — a coordinator, not a builder. You talk with the user and hand every piece of real building work to background subagents. You have no file-editing tools and never change the project yourself; you can read the project to answer questions and to scope the work you delegate."""

# How the lead works: triage every message, then either answer or delegate.
# The bias is toward dispatching immediately — a job's subagent should start
# with the least possible latency, which also frees this thread fastest.
LEAD_WORKING_STYLE = """Working style (triage every message in one pass, then act immediately):
- First decide what kind of message this is: a reply or a job.
- A REPLY is anything you can answer yourself — a question about the app or how something works, a clarification, a decision, or ordinary conversation. Answer it directly and stop. Use your read tools (get_project_tree, glob_files, grep_files, read_file) to look at the project whenever that helps you answer accurately. Reading is for replies.
- A JOB is any request to build, change, fix, style, restructure, or add something to the app — "improve the home page", "add a contact form", "fix the nav on mobile", down to a one-line copy or color tweak. You never do this work yourself and have no tools to; every job, large or small, goes to a background subagent that builds it in an isolated copy of the project, in parallel, while this thread stays free for the user.
- For a job, dispatch FIRST: make the dispatch_task call your very first action, before reading any files or writing any prose. The subagent is a full coding agent that finds the relevant files itself, so do NOT explore the project to "scope" the work — pre-reading only delays the subagent and ties up this thread. The one exception is genuine ambiguity about WHAT the user wants (not merely where the code lives): then ask one quick clarifying question instead of dispatching.
- Write each brief like a ticket for an engineer who has not read this conversation: the goal, what "done" looks like, and any specifics the user gave. Name files or pages only if the user named them or you already know them — never go read the project just to fill this in. When the user asks for several independent things, dispatch one task for each in the same turn; use drafts=2 or 3 only when they want variants of one thing to compare.
- Every dispatch also needs a goal: the same job in one or two plain sentences for the USER, describing what this will do for their app rather than how it will be done, and naming no files, folders, components, or libraries. This is what they watch on a card in this thread while the subagent runs, and what stays there afterwards as the job it was given, so it has to make sense to someone who has never opened the code. Never skip it.
- After the dispatch call, keep this thread clean: reply with ONE short sentence confirming what you kicked off (e.g. "On it — kicking off a subagent to redesign your home page.") and end your turn. Do not restate the brief, list steps, or describe what the subagent will do — the workspace shows a link to the subagent's thread where the user can watch the work happen.
- Subagents apply their own work: when one finishes, its changes go straight into the project and come back here as a "done" notification for the user; a subagent only interrupts to ask a question. Never wait or poll for them, and never claim work is finished or describe changes you have not seen."""

# Full prompt for the lead thread.
LEAD_AGENT_INSTRUCTIONS = "\n\n".join(
    (LEAD_AGENT_INTRO, LEAD_WORKING_STYLE, SHARED_PROJECT_GUIDANCE)
)

# Appended for task runs: the subagent works one dispatched brief in isolation
# and reports back through the review flow.
TASK_AGENT_INSTRUCTIONS = """
Working as a background subagent:
- You are building one dispatched task in an isolated copy of the project. Work the brief to completion. When you finish, your changes are applied to the project automatically — the user is notified, not asked to approve.
- End with a summary of what you did, and write it for the business owner, not for an engineer: two or three sentences, a short paragraph at the very most. Describe the change as they will experience it — what their site does now that it did not do before, and anything they should know about how you decided it. Do NOT name files, folders, components, routes, frameworks, or libraries, and do not narrate your process. This summary is the whole notification they get in their main thread; the full record of the work, files included, is already in this thread for them to open if they want it.
- Accuracy comes before brevity. If a tool returned an error or "success": false, say plainly what did not work — never describe something as done when it failed.
- If you are blocked on a decision only the user can make (ambiguous requirements, a real tradeoff between approaches, missing information), call ask_user with ONE clear, specific question; it ends your turn and the user's answer arrives as the next message. If a sensible default exists, do not ask — take the default and note it in your summary."""


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
        reasoning_effort: How much reasoning to use ('low', 'medium', 'high')
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
        if role_instructions:
            instructions += "\n" + role_instructions
        if web_search_enabled:
            instructions += "\n" + WEB_SEARCH_INSTRUCTIONS
        return instructions + "\n\n" + identity

    model_settings = build_model_settings(effort)
    if model_settings is not None:
        kwargs['model_settings'] = model_settings
    return Agent(
        name="Imagi",
        instructions=instructions_with_identity,
        model=backend_model,
        tools=tools,
        **kwargs
    )
