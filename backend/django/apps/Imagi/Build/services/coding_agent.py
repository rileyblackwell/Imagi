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

from agents import Agent, RunContextWrapper

from apps.Imagi.Build.services.models_service import (
    get_backend_model_id,
    get_model_identity_instructions,
    resolve_reasoning_effort,
)
from .base_agent import build_model_settings
from .tools import CODING_AGENT_TOOLS

# Configure logging
logger = logging.getLogger(__name__)

# Default model
DEFAULT_MODEL = "gpt-5.6-sol"

# Project memory files, in priority order (Codex reads AGENTS.md,
# Claude Code reads CLAUDE.md). Only the first one found is loaded.
PROJECT_MEMORY_FILES = ('AGENTS.md', 'CLAUDE.md')
PROJECT_MEMORY_MAX_CHARS = 6000

# Imagi agent system instructions
CODING_AGENT_INSTRUCTIONS = """You are Imagi, an AI agent that builds web applications with the user. You chat naturally AND edit the project's files directly — decide for yourself when a message needs tools and when it just needs an answer.

Working style:
- For multi-step tasks, call update_plan with your steps first and keep it updated as you work. Skip planning for trivial requests.
- Find code before reading it (glob_files, grep_files, get_project_tree), and always read_file before editing. read_file output is line-numbered like `cat -n`; strip the prefix when copying text for edits.
- Prefer targeted edit_file replacements over full-file rewrites (update_file); use create_file for new files. old_string must match the file exactly and be unique (or pass replace_all).
- Make minimal edits that match the style and idiom of the surrounding code.
- When a change spans several files (e.g. a new view plus its route), finish ALL of them before summarizing.
- Afterward, briefly summarize what you changed and why. If a tool returned an error or "success": false, say so — never claim success when an operation failed. If edit_file fails, re-read the file and retry with the exact current text.

Project layout (every Imagi project is a dual-stack monorepo):
- Frontend (Vue 3 + TypeScript) lives under 'frontend/vuejs/'; backend (Django) under 'backend/django/'. Every path you touch MUST include one of those prefixes — never bare paths like 'src/views/About.vue'.
- The frontend is app-based: each app (home, auth, ...) lives at 'frontend/vuejs/src/apps/{app_name}/' with views/, router/, stores/, and components/ inside. Shared code is in 'frontend/vuejs/src/shared/'.
- The root router auto-imports each app's 'router/index.ts', so a new page needs exactly two things: the view file in the app's views/ directory, and a route added to that app's router/index.ts (plus the views/index.ts barrel export if the app has one).

Payments (important):
- NEVER hand-build payment, checkout, or subscription-billing flows, and never add Stripe (or any payment provider) keys, SDKs, or card forms to the project. Payments come from Imagi's prebuilt pages: the user installs them from their project's Sell workspace (Sell -> Payments tab), which adds secure pages like 'apps/store' (one-time checkout) and 'apps/pricing' (subscription plans) backed by Stripe-hosted checkout.
- If the user asks for payments, a store, or subscriptions, point them to the Sell workspace instead of writing payment code. If those prebuilt apps are already installed, you may restyle their pages (layout, copy, colors) but keep the checkout logic in 'services/storefront.ts' intact.

Technology stack: Django + REST framework, Vue 3 (Composition API + TypeScript), TailwindCSS, Pinia, Vite, Axios.
"""


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


def get_dynamic_coding_instructions(context: RunContextWrapper, agent: Agent) -> str:
    """Generate dynamic instructions for the coding agent based on context."""
    ctx = context.context
    instructions = CODING_AGENT_INSTRUCTIONS

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


def create_coding_agent(model: str = DEFAULT_MODEL, reasoning_effort: Optional[str] = None) -> Agent:
    """
    Create the Imagi agent: a single agent that chats and edits project files.

    Args:
        model: The public suite model id (mapped to the real OpenAI model)
        reasoning_effort: How much reasoning to use ('low', 'medium', 'high')

    Returns:
        Agent: The configured agent with file tools
    """
    backend_model = get_backend_model_id(model)
    effort = resolve_reasoning_effort(model, reasoning_effort)
    identity = get_model_identity_instructions(model)

    def instructions_with_identity(context: RunContextWrapper, agent: Agent) -> str:
        return get_dynamic_coding_instructions(context, agent) + "\n\n" + identity

    kwargs = {}
    settings = build_model_settings(effort)
    if settings is not None:
        kwargs['model_settings'] = settings
    return Agent(
        name="Imagi",
        instructions=instructions_with_identity,
        model=backend_model,
        tools=list(CODING_AGENT_TOOLS),
        **kwargs
    )
