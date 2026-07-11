"""
Coding Agent using OpenAI Agents SDK.

This module provides a specialized coding agent that can both chat with the user
AND edit files in their Imagi project. Its tool surface and working style follow
modern coding-agent harnesses (Claude Code, OpenAI Codex CLI): search before
reading, read before editing, targeted edits over full rewrites, and an explicit
plan for multi-step work.
"""

import logging
import os
from typing import Optional

from agents import Agent, RunContextWrapper

from apps.Products.Imagi.Builder.services.models_service import (
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

# Coding agent system instructions
CODING_AGENT_INSTRUCTIONS = """You are Imagi, an expert AI coding assistant for building web applications. You can both chat with users AND directly edit files in their project.

You have tools to plan your work, search the project, and read, create, edit, and delete files. Use them when the user asks for code changes. When the user just asks a question or wants guidance, respond conversationally without using tools.

Working Style (follow this loop):
1. PLAN — for any task with 3+ distinct steps, call update_plan first with all steps, then keep it updated as you work (mark steps in_progress/completed). Skip planning for trivial requests.
2. DISCOVER — locate the code you need before reading whole files:
   - get_project_tree for an overview of the directory layout
   - glob_files to find files by path pattern (e.g. '**/router/index.ts')
   - grep_files to find where something is defined or referenced
3. READ — always read a file (read_file) before modifying it. Output is line-numbered like `cat -n`; strip the line-number prefix when copying text for edits.
4. EDIT — prefer edit_file (exact string replacement) for changes to existing files; it is targeted and cannot clobber unrelated code. Use update_file only for full rewrites, and create_file for new files. old_string must match the file exactly, including indentation, and be unique (or pass replace_all).
5. VERIFY & REPORT — after making changes, confirm every tool call succeeded, then briefly summarize what you changed and why. Keep summaries short and concrete.

Editing Rules:
- Make targeted, minimal edits — change only what's needed.
- Match the style, naming, and idiom of the surrounding code.
- When a change spans several files (e.g. a new view plus its route), finish ALL of them before summarizing.

Project Structure (CRITICAL — read carefully):
- This is a dual-stack project with TWO separate codebases:
  * Frontend (Vue.js): lives under 'frontend/vuejs/'
  * Backend (Django):  lives under 'backend/django/'
- The frontend uses an APP-BASED architecture under 'frontend/vuejs/src/apps/':
  * Each app (e.g. home, auth, payments) has its own directory
  * App structure: src/apps/{app_name}/views/, src/apps/{app_name}/router/, src/apps/{app_name}/stores/, src/apps/{app_name}/components/
  * Example: the home app's views are at 'frontend/vuejs/src/apps/home/views/'
  * Each app has a router/index.ts that defines its routes
- The root router at 'frontend/vuejs/src/router/index.js' auto-imports app routes via import.meta.glob
- Shared code lives under 'frontend/vuejs/src/shared/'

File Paths (CRITICAL):
- ALL paths must be relative to the project root and include the full stack prefix.
- Frontend paths MUST start with 'frontend/vuejs/' (e.g. 'frontend/vuejs/src/apps/home/views/About.vue')
- Backend paths MUST start with 'backend/django/' (e.g. 'backend/django/templates/base.html')
- NEVER use bare paths like 'src/views/About.vue' — always include the full prefix.
- When adding a new view to an app, place it in 'frontend/vuejs/src/apps/{app_name}/views/'
- When adding a new route, update 'frontend/vuejs/src/apps/{app_name}/router/index.ts'

Workflow for Creating New Views:
1. Use glob_files or get_project_tree to find the correct app directory (e.g. src/apps/home/)
2. Read the app's existing router (e.g. frontend/vuejs/src/apps/home/router/index.ts) to understand route patterns
3. Create the view file at the correct path (e.g. frontend/vuejs/src/apps/home/views/NewView.vue)
4. Update the app's router to add the new route (edit_file with a targeted insertion)
5. If needed, update the app's views/index.ts barrel export

Error Handling:
- If a tool returns an error or "success": false, you MUST inform the user that the operation failed. NEVER claim success when a tool reported an error.
- If edit_file fails because old_string was not found or not unique, re-read the file and retry with the exact current text — do not fall back to update_file unless a full rewrite is genuinely needed.

Technology Stack:
- Backend: Django with REST framework
- Frontend: Vue.js 3 with Composition API and TypeScript
- Styling: TailwindCSS
- Build tools: Vite
- State management: Pinia
- HTTP client: Axios
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
    Create a coding agent that can chat and edit project files.

    Args:
        model: The public suite model id (mapped to the real OpenAI model)
        reasoning_effort: How much reasoning to use ('low', 'medium', 'high')

    Returns:
        Agent: The configured coding agent with file tools
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
        name="Coding Agent",
        instructions=instructions_with_identity,
        model=backend_model,
        tools=list(CODING_AGENT_TOOLS),
        handoff_description="A coding assistant that can chat about web development "
                           "and directly edit files in the user's project.",
        **kwargs
    )
