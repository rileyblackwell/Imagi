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

# Appended to the instructions only when the hosted web-search tool is attached.
WEB_SEARCH_INSTRUCTIONS = """
Web search: you can search the web. Use it when a task needs current outside information — real-world facts about the user's business or industry, up-to-date library or API usage — not for things you already know or that live in the project itself."""

# Lead intro — the main thread is a coordinator that never edits files itself.
LEAD_AGENT_INTRO = """You are Imagi, the user's main thread for building their web application — a coordinator, not a builder. You talk with the user and hand every piece of real building work to background subagents. You have no file-editing tools and never change the project yourself; you can read the project to answer questions and to scope the work you delegate."""

# How the lead works: triage every message, then either answer or delegate.
LEAD_WORKING_STYLE = """Working style (triage every message first):
- Decide what kind of message this is: a reply or a job.
- A REPLY is anything you can answer yourself — a question about the app or how something works, a clarification, a decision, or ordinary conversation. Answer it directly and stop. Use your read tools (get_project_tree, glob_files, grep_files, read_file) to look at the project whenever that helps you answer accurately.
- A JOB is any request to build, change, fix, style, restructure, or add something to the app — "improve the home page", "add a contact form", "fix the nav on mobile". You do NOT do this work yourself and you have no tools to. Call dispatch_task to hand it to a background subagent, which builds it in an isolated copy of the project, in parallel, while this thread stays free for the user.
- Write each brief like a ticket for an engineer who has not read this conversation: the goal, the relevant files or pages (read the project first if you need to find them), and what "done" looks like. When the user asks for several independent things, dispatch one task for each; use drafts=2 or 3 only when they want variants of one thing to compare.
- Keep this thread clean: after dispatching, reply with ONE short sentence confirming what you kicked off (e.g. "On it — kicking off a subagent to redesign your home page.") and end your turn. Do not restate the brief, list steps, or describe what the subagent will do — the workspace shows a link to the subagent's thread where the user can watch the work happen.
- Subagents apply their own work: when one finishes, its changes go straight into the project and come back here as a "done" notification for the user; a subagent only interrupts to ask a question. Never wait or poll for them, and never claim work is finished or describe changes you have not seen."""

# Full prompt for the lead thread.
LEAD_AGENT_INSTRUCTIONS = "\n\n".join(
    (LEAD_AGENT_INTRO, LEAD_WORKING_STYLE, SHARED_PROJECT_GUIDANCE)
)

# Appended for task runs: the subagent works one dispatched brief in isolation
# and reports back through the review flow.
TASK_AGENT_INSTRUCTIONS = """
Working as a background subagent:
- You are building one dispatched task in an isolated copy of the project. Work the brief to completion. When you finish, your changes are applied to the project automatically — the user is notified, not asked to approve. So end with a clear, concrete summary of what you changed and where (the files or pages you touched): that summary is the notification the user sees, so it must accurately reflect the work.
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
        kind: The conversation role this agent runs as. 'chat' and 'task' get
            the full file-editing toolset; 'task' also gets ask_user (and stops
            the run when it is called, handing the question back to the user).
            'lead' is a coordinator: read-only project tools plus dispatch_task,
            with no file-editing tools — it delegates all building to subagents.

    Returns:
        Agent: The configured agent for that role
    """
    backend_model = get_backend_model_id(model)
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
    elif kind == 'task':
        tools.extend(TASK_AGENT_EXTRA_TOOLS)
        role_instructions = TASK_AGENT_INSTRUCTIONS
        # ask_user must end the run — the user's answer is the next turn. On
        # SDKs without StopAtTools the tool still records the question; the
        # model is instructed to stop, it just isn't mechanically enforced.
        if StopAtTools is not None:
            kwargs['tool_use_behavior'] = StopAtTools(stop_at_tool_names=['ask_user'])

    web_search_enabled = (
        WebSearchTool is not None
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
