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

try:  # Ends a run after a named tool call (task runs stop on ask_user)
    from agents.agent import StopAtTools
except ImportError:  # pragma: no cover - defensive fallback
    StopAtTools = None

from apps.Imagi.Build.services.models_service import (
    get_backend_model_id,
    get_model_by_id,
    get_model_provider,
    resolve_reasoning_effort,
    supports_fast_mode,
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
DEFAULT_MODEL = _BUILDER_SETTINGS.get('DEFAULT_MODEL', 'claude-opus-5-5')

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
# throughput, and the 'fast' tier (GPT 6's name for what earlier models
# called 'priority') roughly doubles it. None leaves the account default.
INITIAL_BUILD_SERVICE_TIER = _BUILDER_SETTINGS.get('INITIAL_BUILD_SERVICE_TIER')

# The Claude counterpart: fast mode (speed 'fast') for the first build, on a
# model that has it (Opus 5.5). Faster output at twice the price per token —
# worth it on the one run a founder is watching a clock on. None turns it off.


def run_speed(kind: str, model: str, fast_mode: bool = False) -> Optional[str]:
    """The speed a run's requests ask for on a model: 'fast' when the run
    asks for fast mode (the user's switch, or the first build's home page) on
    a model that offers it; otherwise None (standard). ``kind`` is accepted so
    a role-specific speed has one place to land."""
    del kind
    if fast_mode and supports_fast_mode(model):
        return 'fast'
    return None

# Project memory files, in priority order (Codex reads AGENTS.md,
# Claude Code reads CLAUDE.md). Only the first one found is loaded.
PROJECT_MEMORY_FILES = ('AGENTS.md', 'CLAUDE.md')
PROJECT_MEMORY_MAX_CHARS = 6000

# --- System prompts -----------------------------------------------------------
# Deliberately short: what Imagi is, the agent's role, and the user's project.
# How to use each tool lives in that tool's own description, which is sent
# with every call too, so the prompts don't repeat it.

IMAGI_INTRO = """Imagi lets people, most of them not technical, build a web app for their idea or business by chatting with AI, then run the business with Imagi's Sell, Market and Operate tools."""

# The app every project starts from, for the roles that edit it.
APP_GUIDANCE = """The app is a Vue 3 + TypeScript frontend in frontend/vuejs/ and a Django REST API in backend/django/; all UI is Vue. Sign-in and payments are prebuilt by Imagi, so don't build your own (the user adds payments from the Sell console), and never submit real payments or personal data in the preview."""

LEAD_AGENT_INSTRUCTIONS = f"""You are the coordinator in Imagi's build workspace. {IMAGI_INTRO}

The user chats with you about their app. You never edit files: all building goes to threads, background agents that each own one job, work in their own copy of the project, and apply their changes to the live app when they finish, without asking the user to approve. You can read the project, look at the live preview, and use web_search and explore_project.

For each message:
- A question or conversation: answer it yourself.
- New work: start a thread with dispatch_task, one thread per job, with a brief a developer who hasn't seen this chat could work from. Ask for several drafts only when the user wants options to compare. Then reply in one short sentence.
- Anything about a job a thread already has (a change, more detail, an answer to its question): send it to that thread with message_task, even if it has finished or stopped.
- If what the user wants is unclear, ask with ask_user, with short options when you can.

Each thread shows as a card in this chat while it works. When it ends, a [Thread report] here gives its own words and how it ended: finished and applied, waiting for the user to pick a draft, stopped to ask the user a question, or stopped before finishing. The user already sees each report and question on the card and can answer there or open the thread, so don't repeat them. If the user answers a thread's question here, pass it on with message_task. If a thread stopped before finishing, say so plainly and offer to send it back to work. Errors the app reports go to a thread automatically. Your thread list below shows where each one stands now.

Keep your replies short and plain, with no code or file names. Sign-in and payments come prebuilt; the user adds payments from the Sell console."""

TASK_AGENT_INSTRUCTIONS = f"""You are a thread in Imagi's build workspace. {IMAGI_INTRO}

The coordinator handed you one job from the user; see it through. You work in your own copy of the project, and your changes go into the live app the user is watching as you make them, so check your work in the preview. Later messages here, from the coordinator or from the user directly, steer the same job. An [App error] message means the app reported errors after your change: find out whether you caused them and fix them if so. When a decision is really the user's, call ask_user with one question and short options; it ends your turn and their answer arrives as the next message. Otherwise pick a sensible default and mention it.

{APP_GUIDANCE}"""

# Appended last for a thread, after the project context, so it is the
# freshest instruction when the run ends: that message is the card the user
# reads.
TASK_SIGN_OFF = """Your final message is this thread's summary for the user: a short paragraph in everyday words about what changed in their app, with no code or file names, and plain about anything that didn't work."""

# The legacy single-agent chat role (no coordinator), kept for old
# conversations.
CODING_AGENT_INSTRUCTIONS = f"""You are Imagi's builder. {IMAGI_INTRO}

You chat with the user about their app and edit its files directly. Tell them what changed in plain words, and say plainly if something didn't work.

{APP_GUIDANCE}"""

# The first build: one page per thread, in parallel, against the clock. The
# rules here are the ones a page is discarded for breaking, so they stay.
# The business itself arrives in the page's brief.
INITIAL_BUILD_INSTRUCTIONS = f"""You are a thread in Imagi's build workspace, building one page of a brand-new app while other threads build the rest. {IMAGI_INTRO} Your brief names your page.

Rewrite only that page's view file, in a single write, as a real, custom-looking page for this business. Touching any other file collides with the other threads, and a page that references a missing file is thrown away. There are no image files: use CSS and inline SVG. For header and footer links, import sitePages from '../site-pages' and loop over it. You have about {INITIAL_BUILD_TIME_BUDGET_S} seconds, so aim for 8 KB (under 10 KB), one light theme, and no payments or backend calls.

Then tell the founder in four to six plain sentences what the page offers a visitor."""


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


def project_context(ctx) -> str:
    """The user's app as they described it when creating the project: its
    name, what it is, how it works and how it should look."""
    fields = (
        ('Name', getattr(ctx, 'project_name', None)),
        ('What it is', getattr(ctx, 'project_description', None)),
        ('How it works', getattr(ctx, 'project_app_details', None)),
        ('Look and feel', getattr(ctx, 'project_design', None)),
    )
    lines = [
        f"{label}: {' '.join(str(value).split())}"
        for label, value in fields if value and str(value).strip()
    ]
    if not lines:
        return ''
    return "The user's app:\n" + "\n".join(lines)


def get_dynamic_coding_instructions(
    context: RunContextWrapper,
    agent: Agent,
    base_instructions: str = CODING_AGENT_INSTRUCTIONS,
) -> str:
    """The role's static prompt plus this run's context: the user's project,
    the file they have open, the coordinator's thread roster, and the
    project's memory file."""
    ctx = context.context
    instructions = base_instructions
    if not ctx:
        return instructions

    project = project_context(ctx)
    if project:
        instructions += "\n\n" + project

    current_file = getattr(ctx, 'current_file', None) or {}
    if current_file.get('path'):
        instructions += f"\n\nThe user has {current_file['path']} open."

    # The coordinator's threads and where each stands — what lets it route a
    # follow-up to the thread already on that job and answer status questions.
    roster = getattr(ctx, 'task_roster', '')
    if roster:
        instructions += "\n\n" + roster

    memory = load_project_memory(getattr(ctx, 'project_path', None))
    if memory:
        instructions += f"\n\n{memory}"

    return instructions



def build_agent_model(model: str):
    """
    What the Agent's `model` is for a public model id: the real OpenAI model id
    (a string, which the SDK serves through the Responses API) for GPT models,
    or an AnthropicModel for Claude models.
    """
    backend_model = get_backend_model_id(model)
    if get_model_provider(model) == 'anthropic':
        from .anthropic_model import AnthropicModel
        definition = get_model_by_id(model) or {}
        return AnthropicModel(
            backend_model,
            refusal_fallback=bool(definition.get('refusal_fallback')),
        )
    return backend_model


def create_coding_agent(
    model: str = DEFAULT_MODEL,
    reasoning_effort: Optional[str] = None,
    kind: str = 'chat',
    fast_mode: bool = False,
) -> Agent:
    """
    Create the Imagi agent for a given conversation role.

    Args:
        model: The public model id (mapped to the real OpenAI or Anthropic model)
        reasoning_effort: How much reasoning to use — one of the platform ladder
            ('low', 'medium', 'high', 'xhigh'), the same for every model;
            legacy or unknown values are re-seated by resolve_reasoning_effort
        kind: The conversation role this agent runs as. 'chat', 'task', and
            'initial_build' get the full file-editing toolset; 'task' also gets
            ask_user (and stops the run when it is called, handing the question
            back to the user). 'initial_build' is the one-shot first build of a
            new project — same tools as chat, but a first-build prompt with
            design direction. 'lead' is a coordinator: read-only project tools
            plus dispatch_task (new work) and message_task (follow-ups to a
            subagent it already has), with no file-editing tools — it delegates
            all building to subagents.
        fast_mode: Ask for Claude's fast mode (see run_speed); ignored on a
            model that doesn't offer it.

    Returns:
        Agent: The configured agent for that role
    """
    # The coordinator runs at the effort picked in its own composer, like any
    # thread (default Medium); only the first build pins its own.
    if kind == 'initial_build':
        reasoning_effort = INITIAL_BUILD_REASONING_EFFORT
    effort = resolve_reasoning_effort(model, reasoning_effort)

    tools = list(CODING_AGENT_TOOLS)
    base_instructions = CODING_AGENT_INSTRUCTIONS
    role_instructions = ""
    kwargs = {}
    if kind == 'lead':
        # The lead coordinates but never builds: read-only tools plus
        # dispatch_task and message_task, and no file-editing tools at all.
        # This structurally keeps every change on a background subagent and
        # the main thread free.
        tools = list(LEAD_AGENT_READONLY_TOOLS) + list(LEAD_AGENT_EXTRA_TOOLS)
        base_instructions = LEAD_AGENT_INSTRUCTIONS
        # The coordinator's clarifying question ends its turn the same way a
        # thread's does: the user's answer (a tap on an option, or typed) is
        # the next message.
        if StopAtTools is not None:
            kwargs['tool_use_behavior'] = StopAtTools(stop_at_tool_names=['ask_user'])
    elif kind == 'initial_build':
        # One-shot first build of a new project: same full editing toolset as
        # chat, but framed as the initial build with explicit design direction.
        base_instructions = INITIAL_BUILD_INSTRUCTIONS
    elif kind == 'task':
        tools.extend(TASK_AGENT_EXTRA_TOOLS)
        base_instructions = TASK_AGENT_INSTRUCTIONS
        role_instructions = TASK_SIGN_OFF
        # ask_user must end the run — the user's answer is the next turn. On
        # SDKs without StopAtTools the tool still records the question; the
        # model is instructed to stop, it just isn't mechanically enforced.
        if StopAtTools is not None:
            kwargs['tool_use_behavior'] = StopAtTools(stop_at_tool_names=['ask_user'])

    # Web search and project exploration run on Haiku (helper_tools), so
    # the legwork never bills at the agent's own rate. The initial build is
    # the one role without them: it is racing a wall-clock budget, and
    # everything it needs is in the founder's brief.
    helpers_enabled = (
        kind != 'initial_build'
        and _BUILDER_SETTINGS.get('ENABLE_WEB_SEARCH', True)
    )
    if helpers_enabled:
        from .helper_tools import HELPER_TOOLS
        tools.extend(HELPER_TOOLS)

    # The preview browser, for the same roles: the coordinator and threads
    # can look at and use the running app the way the user does. It is a
    # Claude toolset, so only Claude models get it; the first build has no
    # time for it, and nothing to look at yet.
    browser_enabled = (
        kind != 'initial_build'
        and get_model_provider(model) == 'anthropic'
        and _BUILDER_SETTINGS.get('ENABLE_PREVIEW_BROWSER', True)
    )
    if browser_enabled:
        from .preview_browser_tool import preview_browser_tool
        tools.append(preview_browser_tool())

    def instructions(context: RunContextWrapper, agent: Agent) -> str:
        # The first build's brief already carries the business, so its
        # prompt takes no run context.
        if kind == 'initial_build':
            return base_instructions
        text = get_dynamic_coding_instructions(context, agent, base_instructions)
        if role_instructions:
            text += "\n\n" + role_instructions
        return text

    # The lead's tool calls have side effects it cannot see until they return:
    # one dispatch_task call creates a subagent that starts editing the project.
    # Left parallel, a single assistant message can carry the same dispatch
    # twice — two subagents on one job, each overwriting the other's merge — so
    # the lead calls its tools one at a time and sees each result before the
    # next. Builders are unaffected: their parallel reads and edits are wanted.
    #
    # The first build alone asks for a faster tier (OpenAI's service tier,
    # Claude's fast mode): it is the one run a person is watching a clock
    # on, and the tier is priced per token.
    model_settings = build_model_settings(
        effort,
        parallel_tool_calls=False if kind == 'lead' else None,
        service_tier=(
            INITIAL_BUILD_SERVICE_TIER
            if kind == 'initial_build' and get_model_provider(model) == 'openai' else None
        ),
        speed=run_speed(kind, model, fast_mode),
    )
    if model_settings is not None:
        kwargs['model_settings'] = model_settings
    return Agent(
        name="Imagi",
        instructions=instructions,
        model=build_agent_model(model),
        tools=tools,
        **kwargs
    )
