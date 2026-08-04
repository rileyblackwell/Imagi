"""
Base Agent Service using OpenAI Agents SDK.

This module provides the agent harness for the Imagi workspace: it owns
conversation persistence, context construction (including automatic history
compaction), the agent run loop, and extraction of structured run metadata
(plan, tool calls, changed files) for the workspace UI.
"""

import json
import os
import re
import logging
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from dotenv import load_dotenv

from agents import Agent, MaxTurnsExceeded, Runner, RunConfig
from asgiref.sync import sync_to_async

try:  # ModelSettings location can vary across SDK versions
    from agents import ModelSettings
except ImportError:  # pragma: no cover - defensive fallback
    ModelSettings = None

try:  # Run lifecycle hooks (used for the initial build's cost/time caps)
    from agents import RunHooks
except ImportError:  # pragma: no cover - defensive fallback
    RunHooks = None

try:  # Reasoning config for the OpenAI Responses API
    from openai.types.shared import Reasoning
except ImportError:  # pragma: no cover - defensive fallback
    Reasoning = None

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone

from ..models import AgentConversation, AgentMessage, SystemPrompt
from .models_service import compute_cost_usd

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Get API key
OPENAI_API_KEY = os.getenv('OPENAI_KEY') or getattr(settings, 'OPENAI_KEY', None)

# Platform defaults for every user's project (see IMAGI_BUILDER in
# imagi/settings.py); fallbacks keep tests and scripts working without it.
_BUILDER_SETTINGS = getattr(settings, 'IMAGI_BUILDER', {})

# Default model for agents
DEFAULT_MODEL = _BUILDER_SETTINGS.get('DEFAULT_MODEL', 'gpt-5.6-terra')

# Upper bound on agent-loop iterations for a single request: room for
# plan → search → read → edit → verify cycles without letting a confused
# run spin forever.
MAX_AGENT_TURNS = _BUILDER_SETTINGS.get('MAX_AGENT_TURNS', 30)

# Refresh the running-run marker at most this often while stream events flow,
# so the API's staleness window measures silence since the last event rather
# than total run duration (legitimate runs can outlive the window).
RUN_HEARTBEAT_INTERVAL = 60

# Character budget for conversation history sent to the model. When exceeded,
# older messages are compacted into a short summary (auto-compaction, like
# Claude Code) so long-running conversations keep working instead of growing
# without bound.
HISTORY_MAX_CHARS = 60_000
COMPACTED_SNIPPET_CHARS = 120

# How many file paths a capped run's note lists before summarizing the rest.
CAPPED_NOTE_MAX_FILES = 12

# Model used to auto-name a conversation from its opening exchange. Always the
# smallest suite tier (Luna) so naming a thread costs the least usage possible —
# it should never feel like it competes with the build itself. Resolved through
# the registry so it tracks Luna's real backend id if that mapping ever changes.
TITLE_SUITE_MODEL = _BUILDER_SETTINGS.get('TITLE_MODEL', 'gpt-5.6-luna')


def _clean_title(raw: str) -> Optional[str]:
    """Normalize a model-produced title: take the first line, strip any
    "Title:" label and wrapping quotes, collapse whitespace, drop trailing
    punctuation, and cap the length. Returns None when nothing usable remains.
    """
    stripped = (raw or "").strip()
    if not stripped:
        return None
    title = stripped.splitlines()[0]
    # Drop a leading "Title:" / "Title -" style label and any wrapping quotes.
    title = re.sub(r'^\s*title\s*[:\-]\s*', '', title, flags=re.IGNORECASE)
    title = title.strip().strip('"\'“”‘’').strip()
    title = re.sub(r'\s+', ' ', title).rstrip('.!,;:')
    return title[:80] or None


def generate_conversation_title(user_input: str, assistant_reply: str) -> Optional[str]:
    """Ask a small model for a concise title describing the conversation.

    Draws on the opening request and the agent's reply so the name reflects
    what the thread is actually about. Returns a cleaned 3-6 word title, or
    None when unavailable (no key, API error) so the caller can fall back to
    the provisional first-line title.
    """
    if not OPENAI_API_KEY:
        return None
    try:
        from openai import OpenAI

        from .models_service import get_backend_model_id

        client = OpenAI(api_key=OPENAI_API_KEY)
        prompt = (
            "Write a short, specific title for this coding-assistant conversation.\n"
            "Rules: 3-6 words, Title Case, no quotes, no ending punctuation, and "
            "no leading label like 'Title:'. Name the concrete task.\n\n"
            f"User request:\n{(user_input or '').strip()[:800]}\n\n"
            f"Assistant reply:\n{(assistant_reply or '').strip()[:800]}"
        )
        response = client.responses.create(
            model=get_backend_model_id(TITLE_SUITE_MODEL),
            input=prompt,
            max_output_tokens=500,
            reasoning={"effort": "minimal"},
        )
        return _clean_title(getattr(response, "output_text", "") or "")
    except Exception as e:
        logger.warning(f"Conversation title generation failed: {e}")
        return None


class RunBudgetExceeded(Exception):
    """Raised by the cost-budget hook to stop a run that hit its USD cap.

    Used for the initial build so a runaway or unexpectedly large build can't
    spend more than a configured budget. Files written before the cap are
    already on disk, so callers treat this as a partial (capped) result rather
    than a failure.
    """

    def __init__(self, cost_usd: float, budget_usd: float):
        self.cost_usd = cost_usd
        self.budget_usd = budget_usd
        super().__init__(
            f"Run cost ${cost_usd:.4f} reached its ${budget_usd:.2f} budget"
        )


class RunDeadlineExceeded(Exception):
    """Raised by the run-bounds hook when a run runs out of wall-clock time.

    The initial build is bounded primarily by time, not turns: the founder is
    waiting on it, so "how long until I can see my app" is the number that
    matters. Like RunBudgetExceeded this is a partial result, not a failure —
    every file written before the deadline is already on disk.
    """

    def __init__(self, elapsed_s: float, limit_s: float):
        self.elapsed_s = elapsed_s
        self.limit_s = limit_s
        super().__init__(
            f"Run took {elapsed_s:.1f}s, reaching its {limit_s:.0f}s time limit"
        )


def response_has_tool_calls(response) -> bool:
    """Whether a model response asked for tool calls that have yet to run.

    The SDK names every tool item's type with a '_call' suffix ('function_call',
    'file_search_call', ...), and reasoning/message items never end that way, so
    the suffix is a stable test across tool kinds.
    """
    for item in getattr(response, 'output', None) or ():
        item_type = getattr(item, 'type', '') or ''
        if item_type.endswith('_call'):
            return True
    return False


def make_run_bounds_hook(
    model_id: str,
    budget_usd: Optional[float] = None,
    deadline_at: Optional[float] = None,
):
    """A RunHooks that stops a run at its cost and/or wall-clock bound.

    Both are checked after each model turn — the only point the SDK hands us
    control — so a run overshoots by at most the turn in flight.

    A turn that ends over its bound while holding tool calls is allowed to run
    them before the run stops. Raising immediately would throw that turn's work
    away, and for the initial build the turn in flight is usually THE turn: the
    agent spends most of its half-minute generating one large file, and a page
    generated but never written to disk is a build that produced nothing. Tool
    execution is a file write, so waiting for it costs milliseconds.

    deadline_at is an absolute time.monotonic() value, so a multi-run build can
    share one deadline across its runs instead of giving each a fresh budget.

    Returns None when hooks are unavailable or neither bound is usable, so
    callers transparently fall back to the turn cap alone.
    """
    has_budget = bool(budget_usd) and budget_usd > 0
    has_deadline = deadline_at is not None
    if RunHooks is None or not (has_budget or has_deadline):
        return None

    # The hook is built immediately before its run, so this is the run's start.
    started_at = time.monotonic()

    class _RunBoundsHook(RunHooks):
        # Set once a bound is passed on a turn whose tool calls still need to
        # run; raised before the next model turn starts instead.
        deferred_stop = None

        def _exceeded_bound(self, context):
            """The exception for whichever bound this turn passed, if any."""
            if has_deadline:
                now = time.monotonic()
                if now >= deadline_at:
                    return RunDeadlineExceeded(
                        now - started_at, deadline_at - started_at
                    )
            if has_budget:
                usage = getattr(context, 'usage', None)
                input_tokens = getattr(usage, 'input_tokens', 0) or 0
                output_tokens = getattr(usage, 'output_tokens', 0) or 0
                cost = compute_cost_usd(model_id, input_tokens, output_tokens)
                if cost is not None and cost >= budget_usd:
                    return RunBudgetExceeded(cost, budget_usd)
            return None

        async def on_llm_start(self, context, agent, system_prompt, input_items):  # noqa: ANN001
            # The previous turn's tools have run by now, so this is the first
            # moment a deferred stop costs nothing.
            if self.deferred_stop is not None:
                raise self.deferred_stop

        async def on_llm_end(self, context, agent, response):  # noqa: ANN001
            # Reached only on an SDK without on_llm_start: the deferred turn's
            # tools have long since run, so stop here rather than never.
            if self.deferred_stop is not None:
                raise self.deferred_stop
            exceeded = self._exceeded_bound(context)
            if exceeded is None:
                return
            if response_has_tool_calls(response):
                self.deferred_stop = exceeded
                return
            raise exceeded

    return _RunBoundsHook()


def build_model_settings(reasoning_effort: Optional[str] = None):
    """
    Build ModelSettings for an agent, applying a reasoning effort level when one
    is provided (and supported by the installed SDK).

    Returns None when ModelSettings is unavailable, so callers can omit the
    argument entirely and fall back to SDK defaults.
    """
    if ModelSettings is None:
        return None
    if reasoning_effort and Reasoning is not None:
        try:
            return ModelSettings(reasoning=Reasoning(effort=reasoning_effort))
        except Exception as e:  # pragma: no cover - defensive
            logger.warning(f"Could not apply reasoning effort '{reasoning_effort}': {e}")
    return ModelSettings()


def compact_history(messages: List[Dict[str, str]], max_chars: int = HISTORY_MAX_CHARS) -> List[Dict[str, str]]:
    """Compact a conversation history to fit within a character budget.

    Keeps the most recent messages verbatim and replaces older ones with a
    single summary message listing what was discussed, so the model retains
    a thread of the conversation without the full text.
    """
    total = sum(len(m.get("content") or "") for m in messages)
    if total <= max_chars:
        return messages

    # Walk backwards keeping recent messages until the budget is half-spent;
    # the rest of the budget stays available for the summary + new input.
    kept: List[Dict[str, str]] = []
    budget = max_chars // 2
    used = 0
    for msg in reversed(messages):
        size = len(msg.get("content") or "")
        if kept and used + size > budget:
            break
        kept.append(msg)
        used += size
    kept.reverse()

    dropped = messages[:len(messages) - len(kept)]
    if not dropped:
        return kept

    lines = []
    for msg in dropped:
        first_line = (msg.get("content") or "").strip().splitlines()
        snippet = first_line[0][:COMPACTED_SNIPPET_CHARS] if first_line else ""
        lines.append(f"- {msg.get('role', 'user')}: {snippet}")

    summary = (
        f"[Conversation compacted: {len(dropped)} earlier messages were summarized "
        "to fit the context window. One-line summaries of the omitted messages:]\n"
        + "\n".join(lines)
    )
    return [{"role": "user", "content": summary}] + kept


# Argument keys surfaced with tool_call SSE events so the workspace activity
# feed can show what a tool touched. Allowlisted (rather than passing every
# key through) so bulky values like file contents never ride the stream.
_TOOL_ARG_KEYS = ('path', 'file_path', 'pattern', 'query', 'app_name', 'url')
_TOOL_ARG_MAX_CHARS = 200


def extract_tool_args(raw_item) -> Dict[str, str]:
    """Pull a small display-safe subset of a tool call's arguments.

    Defensive by design: raw arguments come straight from the model and may
    be missing, non-JSON, or oddly shaped — a failure here must never break
    the event stream, so any problem just yields {}.
    """
    try:
        raw_args = getattr(raw_item, 'arguments', None)
        if isinstance(raw_args, str):
            parsed = json.loads(raw_args)
        elif isinstance(raw_args, dict):
            parsed = raw_args
        else:
            return {}
        if not isinstance(parsed, dict):
            return {}
        args: Dict[str, str] = {}
        for key in _TOOL_ARG_KEYS:
            value = parsed.get(key)
            if isinstance(value, (str, int, float, bool)):
                args[key] = str(value)[:_TOOL_ARG_MAX_CHARS]
        return args
    except Exception:
        return {}


def extract_run_metadata(result) -> Dict[str, Any]:
    """Extract structured metadata from an Agents SDK run result.

    Returns the names of tools the agent called and the project files it
    changed, so the API can surface the agent's activity to the workspace UI
    (the way Claude Code shows its tool transcript).
    """
    tool_calls: List[str] = []
    files_changed: List[str] = []

    for item in getattr(result, 'new_items', []) or []:
        item_type = getattr(item, 'type', '')

        if item_type == 'tool_call_item':
            raw = getattr(item, 'raw_item', None)
            name = getattr(raw, 'name', None)
            if name:
                tool_calls.append(name)

        # 'function_call_output' kept as a fallback for older SDK versions
        elif item_type in ('tool_call_output_item', 'function_call_output'):
            output = getattr(item, 'output', None)
            try:
                parsed = json.loads(output) if isinstance(output, str) else output
                if isinstance(parsed, dict) and parsed.get("success") and parsed.get("path"):
                    if parsed["path"] not in files_changed:
                        files_changed.append(parsed["path"])
            except (json.JSONDecodeError, TypeError, AttributeError):
                pass

    return {"tool_calls": tool_calls, "files_changed": files_changed}


def extract_tool_call_records(result) -> List[Dict[str, Any]]:
    """Collect [{name, args?}] for every tool call in a run result.

    Richer than extract_run_metadata's name list: keeps the display-safe
    argument subset (extract_tool_args) so persisted metadata can replay the
    workspace activity feed after a reload.
    """
    records: List[Dict[str, Any]] = []
    for item in getattr(result, 'new_items', []) or []:
        if getattr(item, 'type', '') != 'tool_call_item':
            continue
        raw = getattr(item, 'raw_item', None)
        name = getattr(raw, 'name', None)
        if name:
            record: Dict[str, Any] = {"name": name}
            args = extract_tool_args(raw)
            if args:
                record["args"] = args
            records.append(record)
        elif 'web_search' in str(getattr(raw, 'type', '')):
            # Hosted web-search calls carry no .name; use the same synthetic
            # name the tool_call SSE events use.
            records.append({"name": "web_search"})
    return records


def extract_dispatched_tasks(output) -> Optional[List[Dict[str, Any]]]:
    """The dispatch_task tool's staged tasks from a tool output, or None.

    Defensive like extract_tool_args: tool outputs are model-adjacent strings,
    so any parse problem yields None rather than breaking the event stream.
    """
    try:
        parsed = json.loads(output) if isinstance(output, str) else output
        if (
            isinstance(parsed, dict)
            and parsed.get('success')
            and isinstance(parsed.get('dispatched_tasks'), list)
            and parsed['dispatched_tasks']
        ):
            return parsed['dispatched_tasks']
    except (json.JSONDecodeError, TypeError):
        pass
    return None


def extract_usage(result, model_id: str) -> Optional[Dict[str, Any]]:
    """Token usage (with cost when priceable) from an SDK run result, or None.

    The SDK aggregates usage on the run's context wrapper. An all-zero
    reading means nothing was tracked (a real run always spends input
    tokens), so it is treated as unavailable rather than reported as free.
    """
    usage = getattr(getattr(result, 'context_wrapper', None), 'usage', None)
    input_tokens = getattr(usage, 'input_tokens', None)
    output_tokens = getattr(usage, 'output_tokens', None)
    if not isinstance(input_tokens, int) or not isinstance(output_tokens, int):
        return None
    if not input_tokens and not output_tokens:
        return None
    payload: Dict[str, Any] = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    }
    cost = compute_cost_usd(model_id, input_tokens, output_tokens)
    if cost is not None:
        payload["cost_usd"] = cost
    return payload


def _capped_run_note(files_changed: List[str]) -> str:
    """The message a capped run leaves in its thread.

    A build stopped at its cap is the normal way a time-bounded first build
    ends, so the note reports what landed rather than only that a limit was
    hit — that text is what the user reads in the subagent's thread.
    """
    if not files_changed:
        return (
            "I ran out of build time before I could change anything. Tell me "
            "what you'd like me to focus on and I'll get straight to it."
        )
    shown = files_changed[:CAPPED_NOTE_MAX_FILES]
    listed = "\n".join(f"- {path}" for path in shown)
    remaining = len(files_changed) - len(shown)
    if remaining > 0:
        listed += f"\n- …and {remaining} more file{'s' if remaining > 1 else ''}"
    return (
        "I reached this build's time limit and stopped cleanly. Here's what "
        f"I built:\n\n{listed}\n\n"
        "Tell me what you'd like to refine or add next."
    )


def dispatch_task_refs(dispatched: Optional[List[Dict[str, Any]]]) -> Optional[List[Dict[str, Any]]]:
    """Display-safe refs to a run's dispatched tasks, for persisted metadata.

    Keeps just enough to render the transcript's subagent link after a reload
    (the conversation id and title) — the brief already lives on the task
    conversation itself.
    """
    if not dispatched:
        return None
    refs = [
        {"conversation_id": t.get("conversation_id"), "title": t.get("title") or ""}
        for t in dispatched
        if t.get("conversation_id")
    ]
    return refs or None


def build_message_metadata(
    tool_calls: Optional[List[Dict[str, Any]]] = None,
    files_changed: Optional[List[str]] = None,
    plan: Optional[List[Dict[str, str]]] = None,
    usage: Optional[Dict[str, Any]] = None,
    dispatched_tasks: Optional[List[Dict[str, Any]]] = None,
) -> Optional[Dict[str, Any]]:
    """Assemble AgentMessage.metadata from a run's artifacts.

    Empty parts are dropped, and None is returned when nothing is worth
    keeping, so plain conversational replies stay NULL rather than
    accumulating empty {} rows.
    """
    metadata: Dict[str, Any] = {}
    if tool_calls:
        metadata["tool_calls"] = tool_calls
    if files_changed:
        metadata["files_changed"] = files_changed
    if plan:
        metadata["plan"] = plan
    if usage:
        metadata["usage"] = usage
    if dispatched_tasks:
        metadata["dispatched_tasks"] = dispatched_tasks
    return metadata or None


@dataclass
class AgentContext:
    """Context object passed to all agents during a run."""
    user_id: int
    project_id: Optional[int] = None
    project_name: Optional[str] = None
    project_description: Optional[str] = None
    project_path: Optional[str] = None
    # Root directory this run's file tools operate on: the canonical
    # project_path for chat/lead runs, the task's git worktree for
    # kind='task' runs (tools re-point the in-memory Project at it and
    # suppress the DB mirror — see tools._get_project).
    effective_project_path: Optional[str] = None
    conversation_id: Optional[int] = None
    # The conversation's role ('chat' | 'lead' | 'task') — gates the
    # delegation tools (dispatch_task on lead, ask_user on task).
    conversation_kind: Optional[str] = None
    current_file: Optional[Dict[str, Any]] = None
    # Working plan maintained by the agent via the update_plan tool
    plan: List[Dict[str, str]] = field(default_factory=list)
    # Set by a task run's ask_user tool: the question that ended the run,
    # routed into the lead thread's check-in queue instead of marking ready.
    pending_question: Optional[str] = None
    # Tasks staged by the lead's dispatch_task tool during this run
    # ([{conversation_id, title, brief, variant_group, ...}]).
    dispatched_tasks: List[Dict[str, Any]] = field(default_factory=list)


class ImagiAgentService:
    """
    Agent service for the Imagi workspace using OpenAI Agents SDK.

    A single agent (the Imagi agent) handles everything — conversation and
    file editing alike. This service owns conversation persistence, context
    construction, and the run loop around that agent.
    """

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        reasoning_effort: Optional[str] = None,
        agent_kind: Optional[str] = None,
    ):
        """
        Initialize the agent service.

        Args:
            model: The OpenAI model to use (default: gpt-5.6-terra)
            reasoning_effort: How much reasoning the model should use
                ('low', 'medium', 'high'). None uses the model default.
            agent_kind: Run the agent in this role regardless of the
                conversation's own kind. The initial build uses it to get the
                first-build persona (INITIAL_BUILD_INSTRUCTIONS) while its
                conversation stays an ordinary kind='task' — so it keeps the
                worktree isolation, review lifecycle and check-in routing every
                other dispatched task has. None follows the conversation.
        """
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.agent_kind = agent_kind
        # Agents cached per conversation kind: lead runs carry the delegation
        # tool, task runs carry ask_user (+ its stop behavior).
        self._agents: Dict[str, Agent] = {}
        # The kind of the conversation currently being run; set by
        # _prepare_run so the `agent` property builds the right variant.
        self._run_kind: Optional[str] = None

        # Verify API key is available
        if not OPENAI_API_KEY:
            logger.warning("OpenAI API key not found - agent features may not work properly")
        else:
            # Set environment variable for the agents SDK
            os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

    def _apply_reasoning_effort(self, reasoning_effort: Optional[str]) -> None:
        """Update the reasoning effort, invalidating the cached agents if it changed."""
        if reasoning_effort is not None and reasoning_effort != self.reasoning_effort:
            self.reasoning_effort = reasoning_effort
            self._agents = {}

    @property
    def agent(self) -> Agent:
        """Lazy-load the Imagi agent for the current run's conversation kind.

        _prepare_run stamps _run_kind before any caller reaches this, so the
        lead thread gets its delegation tool and task runs get ask_user;
        callers outside a run (tests, scripts) fall back to the plain agent.
        """
        kind = self._run_kind or 'chat'
        if kind not in self._agents:
            from .coding_agent import create_coding_agent
            self._agents[kind] = create_coding_agent(
                self.model, self.reasoning_effort, kind=kind
            )
        return self._agents[kind]

    # -------------------------------------------------------------------------
    # Conversation Management
    # -------------------------------------------------------------------------

    def get_conversation(self, conversation_id: int, user) -> Optional[AgentConversation]:
        """Get an existing conversation by ID."""
        try:
            return get_object_or_404(AgentConversation, id=conversation_id, user=user)
        except Exception as e:
            logger.error(f"Error getting conversation {conversation_id}: {str(e)}")
            return None

    def create_conversation(
        self,
        user,
        model: str,
        system_prompt: Optional[str] = None,
        project_id: Optional[int] = None,
        title: str = "",
        kind: str = "chat",
        parent: Optional[AgentConversation] = None,
        variant_group: str = "",
    ) -> AgentConversation:
        """Create a new conversation. New tasks start awaiting work ('active')."""
        from .coding_agent import CODING_AGENT_INSTRUCTIONS

        conversation = AgentConversation.objects.create(
            user=user,
            model_name=model,
            project_id=project_id,
            mode="agent",
            title=title,
            kind=kind,
            parent=parent,
            review_status='active' if kind == 'task' else '',
            variant_group=variant_group or '',
        )

        prompt_content = system_prompt or CODING_AGENT_INSTRUCTIONS
        SystemPrompt.objects.create(
            conversation=conversation,
            content=prompt_content
        )

        return conversation

    def add_user_message(
        self,
        conversation: AgentConversation,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AgentMessage:
        """Add a user message to the conversation."""
        message = AgentMessage.objects.create(
            conversation=conversation,
            role="user",
            content=content,
            metadata=metadata,
        )
        if not conversation.title:
            conversation.title = (content or "").strip().splitlines()[0][:80]
            conversation.save(update_fields=["title", "updated_at"])
        else:
            conversation.save(update_fields=["updated_at"])
        return message

    def add_assistant_message(
        self,
        conversation: AgentConversation,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AgentMessage:
        """Add an assistant message, with optional run metadata, to the conversation."""
        return AgentMessage.objects.create(
            conversation=conversation,
            role="assistant",
            content=content,
            metadata=metadata,
        )

    def autoname_from_first_reply(
        self,
        conversation: AgentConversation,
        user_input: str,
        response_content: str,
    ) -> Optional[str]:
        """Give the thread a concise AI-generated name off its opening exchange.

        Runs once — only when the just-persisted assistant message is the
        conversation's first reply — so later turns leave the established name
        alone. Skipped for the lead thread: it is simply "the main agent" in
        the workspace and its name is never shown, so naming it would spend a
        model call on a string nobody reads. Returns the new title, or None to
        leave the provisional first-line title (set in add_user_message) in
        place.
        """
        try:
            if getattr(conversation, 'kind', 'chat') == 'lead':
                return None
            if conversation.messages.filter(role="assistant").count() != 1:
                return None
            title = generate_conversation_title(user_input, response_content)
            if not title:
                return None
            conversation.title = title
            conversation.save(update_fields=["title", "updated_at"])
            return title
        except Exception as e:
            logger.warning(f"Auto-naming conversation {conversation.id} failed: {e}")
            return None

    def _record_usage_event(
        self,
        user,
        model: Optional[str],
        usage: Optional[Dict[str, Any]],
        conversation,
    ) -> None:
        """Feed a persisted run's token usage into Payments' usage metering.

        Best-effort by contract: metering must never break message
        persistence, so every failure is swallowed after logging. Runs
        without captured usage are skipped (absent means unknown).
        """
        if not usage:
            return
        try:
            from .usage_limits import record_usage
            record_usage(
                user,
                model or self.model,
                usage.get('input_tokens'),
                usage.get('output_tokens'),
                # Absent when the model had no pricing; Payments then meters
                # the run conservatively instead of treating it as free.
                cost_usd=usage.get('cost_usd'),
                conversation_id=conversation.id if conversation else None,
            )
        except Exception as e:
            logger.warning(f"Could not record usage event: {e}")

    def build_conversation_history(self, conversation: AgentConversation) -> List[Dict[str, str]]:
        """Build conversation history for the agent, compacting when long."""
        messages = []

        history_messages = AgentMessage.objects.filter(
            conversation=conversation
        ).order_by('created_at')

        for msg in history_messages:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

        return compact_history(messages)

    def get_project_info(self, project_id: Optional[int], user) -> Dict[str, Any]:
        """Get project information."""
        project_info = {
            "project_id": project_id,
            "project_name": None,
            "project_description": None,
            "project_path": None,
        }

        if not project_id:
            return project_info

        try:
            from apps.Imagi.ProjectManager.models import Project
            project = Project.objects.get(id=project_id, user=user)
            project_info["project_name"] = project.name
            project_info["project_description"] = getattr(project, 'description', None)
            project_info["project_path"] = getattr(project, 'project_path', None)

            # Make sure the working copy exists on disk before the agent's
            # file tools run: on a production instance (or a fresh dev
            # environment) the files live in the database and must be
            # materialized first.
            try:
                from .project_files_service import ensure_working_copy
                if ensure_working_copy(project):
                    logger.info(f"Hydrated working copy for project {project.id} from database")
            except Exception as e:
                logger.warning(f"Could not ensure working copy for project {project_id}: {e}")
        except Exception as e:
            logger.warning(f"Could not get project info: {e}")

        return project_info

    # -------------------------------------------------------------------------
    # Main Processing
    # -------------------------------------------------------------------------

    def _run_config(self, user) -> RunConfig:
        return RunConfig(
            workflow_name="imagi_agent",
            trace_metadata={"user_id": str(user.id)},
        )

    def _prepare_run(
        self,
        user_input: str,
        user,
        model: Optional[str] = None,
        project_id: Optional[int] = None,
        current_file: Optional[Dict[str, Any]] = None,
        conversation_id: Optional[int] = None,
        reasoning_effort: Optional[str] = None,
        run_state: Optional[Dict[str, Any]] = None,
    ):
        """Resolve the conversation, context and input messages for a run.

        Shared by the blocking and streaming paths. Every database access for a
        run happens here, so the streaming path can perform it in one hop off
        the event loop. ``run_state`` (when given) is filled with the resolved
        conversation before the run marker commits, so a caller whose await was
        cancelled mid-prepare can still clear the marker in its cleanup.
        """
        model = model or self.model
        self._apply_reasoning_effort(reasoning_effort)

        # Get or create conversation
        conversation = None
        if conversation_id:
            conversation = self.get_conversation(conversation_id, user)
        if conversation is None:
            conversation = self.create_conversation(user, model, project_id=project_id)

        # Get project info (also hydrates the working copy, which must exist
        # before the worktree/checkpoint work below can snapshot it)
        project_info = self.get_project_info(project_id, user)

        # Task conversations run inside their own git worktree so parallel
        # tasks (and the lead) never trample each other's edits; every other
        # kind runs on the canonical tree. A worktree failure fails the run —
        # silently running a task on the canonical tree would break isolation.
        effective_root = project_info.get("project_path")
        if conversation.kind == 'task' and effective_root:
            effective_root = self._ensure_task_worktree(conversation, effective_root)

        # A fresh prompt reopens a task that was awaiting review ('ready') or
        # awaiting an answer ('input' — the prompt IS the answer). Any pending
        # check-ins it filed are superseded by this new run: the next run end
        # files fresh ones, so stale queue entries must not linger.
        if conversation.kind == 'task' and conversation.review_status in ('ready', 'input'):
            conversation.review_status = 'active'
            conversation.save(update_fields=["review_status"])
        if conversation.kind == 'task':
            self._resolve_pending_check_ins(conversation)

        # Checkpoint: capture the project state this message starts from, so
        # the workspace can offer a per-message restore point (conversation
        # and files rewind together). Runs against the effective root, so a
        # task's restore points live in its worktree. Best-effort — a
        # checkpoint failure must never block the run itself.
        user_message_metadata = None
        if effective_root:
            try:
                from .version_control_service import VersionControlService
                checkpoint = VersionControlService().ensure_checkpoint(
                    effective_root,
                    'Checkpoint before: ' + (user_input or '').strip().splitlines()[0][:60]
                )
                if checkpoint.get("success") and checkpoint.get("commit_hash"):
                    user_message_metadata = {"checkpoint": checkpoint["commit_hash"]}
            except Exception as e:
                logger.warning(f"Could not create pre-run checkpoint: {e}")

        # Add user message to conversation, stamped with its checkpoint
        user_message = self.add_user_message(
            conversation, user_input, metadata=user_message_metadata
        )
        if run_state is not None:
            # Lets the stream's start event tell the client which persisted
            # message its optimistic bubble became, and its restore point.
            run_state["user_message_id"] = user_message.id
            run_state["checkpoint"] = (user_message_metadata or {}).get("checkpoint")

        context = AgentContext(
            user_id=user.id,
            project_id=project_id,
            project_name=project_info["project_name"],
            project_description=project_info["project_description"],
            project_path=project_info["project_path"],
            effective_project_path=effective_root,
            conversation_id=conversation.id,
            conversation_kind=conversation.kind,
            current_file=current_file,
        )
        # The `agent` property builds the kind-matched variant (delegation
        # tools for lead, ask_user for task) from here on. An explicit
        # agent_kind wins: it selects the persona while the conversation keeps
        # its own kind for isolation and lifecycle.
        self._run_kind = self.agent_kind or conversation.kind

        # Build (compacted) conversation history, excluding the message we
        # just persisted — it is appended as the current input below.
        conversation_history = self.build_conversation_history(conversation)
        if conversation_history and conversation_history[-1]["role"] == "user" \
                and conversation_history[-1]["content"] == user_input:
            conversation_history = conversation_history[:-1]

        input_messages = list(conversation_history)
        input_messages.append({"role": "user", "content": user_input})

        if run_state is not None:
            run_state["conversation"] = conversation

        # Mark the run in flight so conversation endpoints can report
        # is_running; cleared by the caller when the run ends (readers apply
        # a staleness guard in case a crashed worker never clears it).
        # Deliberately the last work in this function: anything raising after
        # this commit — but before the caller's cleanup owns the conversation —
        # would leave the marker set and wedge the project's busy guard.
        # A staged dispatch brief is consumed by the run now firing, so it is
        # cleared in the same commit (the client echoes the brief as the
        # run's user_input).
        run_fields = ["run_started_at"]
        if conversation.queued_prompt:
            conversation.queued_prompt = ''
            run_fields.append("queued_prompt")
        conversation.run_started_at = timezone.now()
        conversation.save(update_fields=run_fields)

        return conversation, context, input_messages

    def _ensure_task_worktree(self, conversation, project_path: str) -> str:
        """Return the task conversation's worktree root, creating it if missing.

        Persists worktree_path on the conversation so the review endpoints
        (accept/dismiss) and cleanup can find it without recomputing.
        """
        from .version_control_service import VersionControlService

        # Task dispatch is exempt from the canonical busy guard, so a live
        # chat/lead run may have half-written edits on the canonical tree
        # right now. Snapshotting them would commit that broken intermediate
        # state as a permanent canonical commit AND fork the task from it,
        # so in that case the task forks from the last committed HEAD instead.
        snapshot_pending = not self._project_has_live_canonical_run(
            conversation.user, conversation.project_id
        )
        result = VersionControlService().create_task_worktree(
            project_path, conversation.id, snapshot_pending=snapshot_pending
        )
        if not result.get('success') or not result.get('worktree_path'):
            raise RuntimeError(
                result.get('message') or 'Could not create the task worktree'
            )
        worktree_path = result['worktree_path']
        if conversation.worktree_path != worktree_path:
            conversation.worktree_path = worktree_path
            conversation.save(update_fields=["worktree_path"])
        return worktree_path

    def _project_has_live_canonical_run(self, user, project_id) -> bool:
        """Is a canonical-tree (chat/lead) run in flight for this project?

        Delegates to the API layer's guard so the staleness window stays
        defined in one place (lazy import: views imports this module at load
        time). Best-effort — an error here must never block a task run.
        """
        if not project_id:
            return False
        try:
            from ..api.views import _project_has_running_conversation
            return _project_has_running_conversation(user, project_id)
        except Exception as e:  # pragma: no cover - defensive
            logger.warning(f"Could not check for a live canonical run: {e}")
            return False

    def _resolve_pending_check_ins(self, conversation) -> None:
        """Best-effort: clear a task's pending queue entries (superseded)."""
        try:
            from ..models import AgentCheckIn
            AgentCheckIn.objects.filter(
                conversation=conversation, status='pending'
            ).update(status='resolved', resolved_at=timezone.now())
        except Exception as e:  # pragma: no cover - best effort
            logger.warning(f"Could not resolve pending check-ins: {e}")

    def _file_check_in(self, conversation, kind: str, body: str) -> None:
        """File one entry into the lead thread's processing queue.

        Best-effort by contract: queueing must never fail the run whose
        outcome it reports. Any older pending entry for the same task is
        resolved first — a task holds at most one live queue slot.
        """
        if getattr(conversation, 'kind', 'chat') != 'task':
            return
        try:
            from ..models import AgentCheckIn
            self._resolve_pending_check_ins(conversation)
            AgentCheckIn.objects.create(
                user=conversation.user,
                project_id=conversation.project_id,
                conversation=conversation,
                lead=conversation.parent,
                kind=kind,
                body=(body or '').strip()[:2000],
            )
        except Exception as e:  # pragma: no cover - best effort
            logger.warning(f"Could not file {kind} check-in: {e}")

    def _finalize_task_run(self, conversation, context, response_content: str) -> None:
        """Route a finished task run back to the main thread.

        A run that ended on ask_user parks the task at 'input' and queues the
        question. A run that finished its work applies itself: a solo task
        auto-merges into the project and queues nothing at all — its 'subagent
        complete' outcome and the summary of what it did live on the dispatch
        card in the main thread, which is a record to read rather than a card
        to clear. Variant
        takes (built to compare) and any task whose auto-merge can't run
        cleanly fall back to a 'ready' review card the user picks or merges by
        hand. Either way the task never interrupts the user directly.
        """
        # getattr: test doubles stand in for the conversation here.
        if getattr(conversation, 'kind', 'chat') != 'task':
            return
        question = (getattr(context, 'pending_question', None) or '').strip() if context else ''
        if question:
            try:
                conversation.review_status = 'input'
                conversation.save(update_fields=["review_status"])
            except Exception as e:  # pragma: no cover - best effort
                logger.warning(f"Could not update task review status: {e}")
            self._file_check_in(conversation, 'question', question)
            return

        # A solo task applies its own work; variants still queue for a
        # pick-one review. _auto_apply_task sets review_status='accepted' on a
        # clean merge, so only the fallback path needs to mark it 'ready'.
        applied = (
            not getattr(conversation, 'variant_group', '')
            and self._auto_apply_task(conversation)
        )
        if applied:
            # Nothing is being asked, so nothing goes in the queue: the work
            # is already in the app and the thread's dispatch card reports it.
            # Any entry an earlier run of this task left behind is stale now.
            self._resolve_pending_check_ins(conversation)
            return
        try:
            conversation.review_status = 'ready'
            conversation.save(update_fields=["review_status"])
        except Exception as e:  # pragma: no cover - best effort
            logger.warning(f"Could not update task review status: {e}")
        self._file_check_in(conversation, 'ready', response_content)

    def _auto_apply_task(self, conversation) -> bool:
        """Merge a finished solo task's worktree into the project automatically.

        Returns True when the changes were applied (the task is now
        'accepted'); False when we deliberately leave it for a manual review —
        a broken frontend import graph, an app router that stopped exporting its
        routes, a first build that dropped its links to the prebuilt auth pages,
        a live canonical run we must not merge across, a merge conflict, a stale
        base, or any git-level failure.
        Best-effort by contract: it never raises, so any trouble simply parks
        the task at 'ready' for the user.
        """
        user = getattr(conversation, 'user', None)
        project_id = getattr(conversation, 'project_id', None)
        # The merge rewrites the canonical tree, so it must not race a chat or
        # lead run editing it — the same guard the accept endpoint applies.
        if user is not None and self._project_has_live_canonical_run(user, project_id):
            return False
        if self._worktree_import_problems(conversation):
            return False
        if self._worktree_router_problems(conversation):
            return False
        if self._worktree_auth_link_problems(conversation):
            return False
        try:
            from ..api.views import _apply_task_worktree, _conversation_project
            project = _conversation_project(conversation)
            if project is None or not getattr(project, 'project_path', ''):
                return False
            return bool(_apply_task_worktree(conversation, project).get('ok'))
        except Exception as e:  # pragma: no cover - best effort
            logger.warning(f"Could not auto-apply task worktree: {e}")
            return False

    def _capped_run_files(self, conversation) -> List[str]:
        """Files a capped run wrote, read back off its working tree.

        A capped run loses the SDK result object that normally reports
        files_changed, but the work itself is on disk — so the tree is the
        record. Only task runs have a worktree to read; a capped chat run
        reports nothing rather than diffing the canonical project. Best-effort:
        never raises into the capped path it is reporting on.
        """
        worktree_path = getattr(conversation, 'worktree_path', '') or ''
        if not worktree_path:
            return []
        try:
            from .version_control_service import VersionControlService
            return VersionControlService().list_worktree_changes(worktree_path)
        except Exception as e:  # pragma: no cover - best effort
            logger.warning(f"Could not list files from a capped run: {e}")
            return []

    def _worktree_import_problems(self, conversation) -> List[Dict[str, str]]:
        """Frontend imports in the task's worktree that point at missing files.

        A run cut short by its turn or cost cap routinely leaves a view or
        route referencing a component it never wrote. Merging that would take
        the project's preview down with a "Failed to resolve import" error, so
        such a task is parked for review instead of applied. Best-effort: if
        the check itself cannot run, it reports no problems rather than
        blocking an otherwise fine merge.
        """
        worktree_path = getattr(conversation, 'worktree_path', '') or ''
        if not worktree_path:
            return []
        try:
            from .frontend_integrity import find_unresolved_imports
            problems = find_unresolved_imports(worktree_path)
        except Exception as e:  # pragma: no cover - defensive
            logger.warning(f"Could not check frontend imports before applying: {e}")
            return []
        if problems:
            logger.warning(
                "Not auto-applying conversation %s: %d unresolved frontend import(s), "
                "first is %s -> %s",
                getattr(conversation, 'id', None),
                len(problems),
                problems[0]['file'],
                problems[0]['import'],
            )
        return problems

    def _worktree_router_problems(self, conversation) -> List[Dict[str, str]]:
        """App router modules in the task's worktree that broke their contract.

        An app router that stops exporting its ``routes`` array — most often by
        being rewritten as a standalone ``createRouter(...)`` — compiles and
        type-checks cleanly, then resolves to no routes at all, so every page
        including the home page 404s. Nothing downstream would catch it, which
        is exactly why it is gated here. Best-effort, like the import check: an
        error reports no problems rather than blocking a fine merge.
        """
        worktree_path = getattr(conversation, 'worktree_path', '') or ''
        if not worktree_path:
            return []
        try:
            from .frontend_integrity import find_router_contract_problems
            problems = find_router_contract_problems(worktree_path)
        except Exception as e:  # pragma: no cover - defensive
            logger.warning(f"Could not check app routers before applying: {e}")
            return []
        if problems:
            logger.warning(
                "Not auto-applying conversation %s: %d app router(s) broke the "
                "routes contract, first is %s (%s)",
                getattr(conversation, 'id', None),
                len(problems),
                problems[0]['file'],
                problems[0]['detail'],
            )
        return problems

    def _worktree_auth_link_problems(self, conversation) -> List[Dict[str, str]]:
        """Prebuilt auth pages the first build's home page stopped linking to.

        Only the initial build is checked, and only it can be: the page it
        rewrites is the scaffold's, which ships those links, so their absence
        means the run dropped them. Later tasks restructure headers for the
        user all the time, and the same check there would fight them.

        Blocking the merge here is how the repair run gets to happen at all —
        it needs the worktree, which the merge removes. It is not the last
        word: initial_build_service ships a page that still fails this rather
        than handing the founder the untouched scaffold. Best-effort, like the
        checks above: an error reports no problems.
        """
        if self.agent_kind != 'initial_build':
            return []
        worktree_path = getattr(conversation, 'worktree_path', '') or ''
        if not worktree_path:
            return []
        try:
            from .frontend_integrity import find_auth_link_problems
            problems = find_auth_link_problems(worktree_path)
        except Exception as e:  # pragma: no cover - defensive
            logger.warning(f"Could not check auth links before applying: {e}")
            return []
        if problems:
            logger.warning(
                "Not auto-applying conversation %s yet: its home page links to "
                "neither %s",
                getattr(conversation, 'id', None),
                " nor ".join(p['path'] for p in problems),
            )
        return problems

    def _clear_run_started(self, conversation) -> None:
        """Best-effort: mark the conversation's run as finished.

        Runs from cleanup paths, so DB errors are swallowed — they must never
        mask the failure (or success) of the run itself.
        """
        try:
            conversation.run_started_at = None
            conversation.save(update_fields=["run_started_at"])
        except Exception as e:  # pragma: no cover - best effort
            logger.warning(f"Could not clear run_started_at: {e}")

    def _touch_run_started(self, conversation) -> None:
        """Best-effort heartbeat: keep the run marker fresh during long runs,
        so the staleness window can't declare a live run finished (which would
        let a second concurrent run onto the project)."""
        try:
            conversation.run_started_at = timezone.now()
            conversation.save(update_fields=["run_started_at"])
        except Exception as e:  # pragma: no cover - best effort
            logger.warning(f"Could not refresh run_started_at: {e}")

    async def process_stream(
        self,
        user_input: str,
        user,
        model: Optional[str] = None,
        project_id: Optional[int] = None,
        current_file: Optional[Dict[str, Any]] = None,
        conversation_id: Optional[int] = None,
        reasoning_effort: Optional[str] = None,
    ):
        """Run the agent, yielding events as they happen.

        Same work as process(), but surfaced incrementally so the workspace can
        show text and tool activity while the run is still going. Yields dicts
        shaped {"type": ..., ...}; the terminal "done" event carries the same
        payload process() returns, so both paths agree on the contract.

        The assistant's reply is persisted even if the client disconnects
        mid-run: the agent has already edited files by then, so dropping the
        message would leave the conversation out of step with the project.
        """
        conversation = None
        context = None
        result = None
        text_parts: List[str] = []
        persisted = False
        # Filled by _prepare_run just before it commits run_started_at: if the
        # awaiting task is cancelled (stop/tab close) while the worker thread
        # is still inside _prepare_run, the tuple assignment below never runs
        # but the marker may already be committed — cleanup resolves the
        # conversation through this holder instead.
        run_state: Dict[str, Any] = {}

        try:
            if not project_id:
                yield {"type": "error", "error": "Project ID is required"}
                return
            if not user_input:
                yield {"type": "error", "error": "Message is required"}
                return

            conversation, context, input_messages = await sync_to_async(self._prepare_run)(
                user_input=user_input,
                user=user,
                model=model,
                project_id=project_id,
                current_file=current_file,
                conversation_id=conversation_id,
                reasoning_effort=reasoning_effort,
                run_state=run_state,
            )

            start_event = {"type": "start", "conversation_id": conversation.id}
            if run_state.get("user_message_id"):
                start_event["user_message_id"] = run_state["user_message_id"]
            if run_state.get("checkpoint"):
                start_event["checkpoint"] = run_state["checkpoint"]
            yield start_event

            # run_streamed returns immediately; the run advances as events are
            # consumed. Sync function tools are dispatched to worker threads by
            # the SDK, so their ORM writes stay off this event loop.
            result = Runner.run_streamed(
                self.agent,
                input=input_messages,
                context=context,
                max_turns=MAX_AGENT_TURNS,
                run_config=self._run_config(user),
            )

            last_heartbeat = time.monotonic()
            async for event in result.stream_events():
                if time.monotonic() - last_heartbeat >= RUN_HEARTBEAT_INTERVAL:
                    last_heartbeat = time.monotonic()
                    await sync_to_async(self._touch_run_started)(conversation)

                if event.type == "raw_response_event":
                    data = getattr(event, 'data', None)
                    if getattr(data, 'type', '') == 'response.output_text.delta':
                        delta = getattr(data, 'delta', '')
                        if delta:
                            text_parts.append(delta)
                            yield {"type": "delta", "text": delta}

                elif event.type == "run_item_stream_event":
                    item = getattr(event, 'item', None)
                    if getattr(item, 'type', '') == 'tool_call_item':
                        raw_item = getattr(item, 'raw_item', None)
                        name = getattr(raw_item, 'name', None)
                        if name:
                            tool_event = {"type": "tool_call", "name": name}
                            args = extract_tool_args(raw_item)
                            if args:
                                tool_event["args"] = args
                            yield tool_event
                            # The plan lives on the context and is rewritten in
                            # place, so re-send it whenever it may have changed.
                            if name == 'update_plan':
                                yield {"type": "plan", "plan": list(context.plan)}
                        elif 'web_search' in str(getattr(raw_item, 'type', '')):
                            # Hosted web-search calls have no .name attribute;
                            # surface them under a stable synthetic name.
                            yield {"type": "tool_call", "name": "web_search"}
                    elif getattr(item, 'type', '') in ('tool_call_output_item', 'function_call_output'):
                        # dispatch_task staged background tasks — tell the
                        # client immediately so it can fire their runs in
                        # parallel while this (lead) run keeps streaming.
                        dispatched = extract_dispatched_tasks(getattr(item, 'output', None))
                        if dispatched:
                            yield {"type": "task_dispatch", "tasks": dispatched}

            response_content = result.final_output or "".join(text_parts)
            metadata = extract_run_metadata(result)
            usage = extract_usage(result, model or self.model)

            await sync_to_async(self.add_assistant_message)(
                conversation,
                response_content,
                build_message_metadata(
                    tool_calls=extract_tool_call_records(result),
                    files_changed=metadata["files_changed"],
                    plan=list(context.plan),
                    usage=usage,
                    dispatched_tasks=dispatch_task_refs(context.dispatched_tasks),
                ),
            )
            persisted = True
            # The final reply landed — route the task back to the main
            # thread: 'ready' for review, or 'input' + a queued question when
            # the run ended on ask_user (partial replies persisted from the
            # finally block below stay 'active').
            await sync_to_async(self._finalize_task_run)(
                conversation, context, response_content
            )
            await sync_to_async(self._record_usage_event)(
                user, model, usage, conversation
            )

            # Name the thread from its opening exchange (once). Emitting the
            # title before "done" lets the sidebar swap the provisional
            # first-line name for the AI one as the run wraps up.
            new_title = await sync_to_async(self.autoname_from_first_reply)(
                conversation, user_input, response_content
            )
            if new_title:
                yield {
                    "type": "title",
                    "title": new_title,
                    "conversation_id": conversation.id,
                }

            done_event = {
                "type": "done",
                "success": True,
                "response": response_content,
                "conversation_id": conversation.id,
                "files_changed": metadata["files_changed"],
                "tool_calls": metadata["tool_calls"],
                "plan": list(context.plan),
                "single_message": True,
            }
            if usage:
                done_event["usage"] = usage
            if context.dispatched_tasks:
                # Backstop for the per-tool task_dispatch events above: a
                # client that missed them mid-stream can still fire the
                # staged runs off the terminal payload.
                done_event["dispatched_tasks"] = list(context.dispatched_tasks)
            yield done_event

        except MaxTurnsExceeded:
            # The run was cut off by the turn cap, not a real failure: the
            # code:'max_turns' lets the frontend offer a "Continue" action
            # (the finally block below keeps the partial reply).
            logger.warning(f"Agent run hit the turn limit ({MAX_AGENT_TURNS} turns)")
            if conversation is not None:
                # A background task's turn-cap must reach the main thread —
                # nobody is watching the task itself.
                await sync_to_async(self._file_check_in)(
                    conversation, 'error',
                    "Ran out of turns before finishing. Progress so far is "
                    "saved — reply to continue this task.",
                )
            yield {
                "type": "error",
                "code": "max_turns",
                "error": (
                    "The agent reached its turn limit before finishing. "
                    "Progress so far is saved — send a message to continue."
                ),
                "conversation_id": conversation.id if conversation else None,
            }
        except Exception as e:
            logger.error(f"Error in imagi_agent stream: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            if conversation is not None:
                # Same routing for failures: a silent dead task would leave
                # the user waiting on a check-in that never comes.
                await sync_to_async(self._file_check_in)(
                    conversation, 'error', f"The task hit an error: {str(e)[:500]}"
                )
            yield {
                "type": "error",
                "error": str(e),
                "conversation_id": conversation.id if conversation else None,
            }
        finally:
            # A cancel can land between _prepare_run's worker thread committing
            # run_started_at and the awaiter resuming; the holder still knows
            # the conversation in that case.
            if conversation is None:
                conversation = run_state.get("conversation")
            # Covers client disconnect (GeneratorExit) and mid-run failure:
            # keep whatever the agent already said rather than losing it.
            if conversation is not None and not persisted:
                partial = "".join(text_parts).strip()
                if partial:
                    try:
                        # The streamed result has accumulated items even when
                        # the run was cut short, so the partial reply keeps
                        # its activity metadata too (usage would be stale
                        # mid-stream, so it is deliberately omitted).
                        partial_metadata = build_message_metadata(
                            tool_calls=extract_tool_call_records(result),
                            files_changed=extract_run_metadata(result)["files_changed"],
                            plan=list(context.plan) if context is not None else None,
                            # A dispatch that happened before the interruption
                            # is real — its subagents are running — so the
                            # transcript keeps their links.
                            dispatched_tasks=dispatch_task_refs(
                                context.dispatched_tasks if context is not None else None
                            ),
                        )
                        await sync_to_async(self.add_assistant_message)(
                            conversation, partial, partial_metadata
                        )
                    except Exception as e:  # pragma: no cover - best effort
                        logger.warning(f"Could not persist partial agent reply: {e}")
                # An interrupted run (stop/disconnect/turn cap) still spent
                # tokens; meter the mid-stream reading — a lower bound, which
                # is honest for the usage windows even though it stays
                # omitted from the displayed message metadata (where absent
                # means unknown).
                try:
                    interrupted_usage = extract_usage(result, model or self.model)
                except Exception:  # pragma: no cover - defensive
                    interrupted_usage = None
                if interrupted_usage:
                    await sync_to_async(self._record_usage_event)(
                        user, model, interrupted_usage, conversation
                    )
            if conversation is not None:
                await sync_to_async(self._clear_run_started)(conversation)

    def process(
        self,
        user_input: str,
        user,
        model: Optional[str] = None,
        project_id: Optional[int] = None,
        current_file: Optional[Dict[str, Any]] = None,
        conversation_id: Optional[int] = None,
        reasoning_effort: Optional[str] = None,
        max_turns: Optional[int] = None,
        cost_budget_usd: Optional[float] = None,
        deadline_at: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Process a message with the Imagi agent.

        The agent both chats and edits project files, deciding on its own when
        to use tools. Persists the message, builds context and (compacted)
        history, runs the agent, and returns the response plus run metadata:
        the files it changed, the tools it called, and its working plan.

        Three optional bounds stop a long run, all treated the same way:
        max_turns overrides the agent-loop cap; cost_budget_usd stops the run
        once its token cost reaches that many dollars; deadline_at (an absolute
        time.monotonic() value) stops it at a wall-clock deadline, which the
        initial build uses so the founder's wait is bounded. A run stopped by
        any of them returns success with "capped": True — the files it produced
        are already on disk.
        """
        if not project_id:
            return {"success": False, "error": "Project ID is required"}

        conversation = None
        context = None
        run_state: Dict[str, Any] = {}
        try:
            if not user_input:
                return {"success": False, "error": "Message is required"}

            conversation, context, input_messages = self._prepare_run(
                user_input=user_input,
                user=user,
                model=model,
                project_id=project_id,
                current_file=current_file,
                conversation_id=conversation_id,
                reasoning_effort=reasoning_effort,
                run_state=run_state,
            )

            run_kwargs: Dict[str, Any] = {}
            bounds_hook = make_run_bounds_hook(
                model or self.model, cost_budget_usd, deadline_at
            )
            if bounds_hook is not None:
                run_kwargs["hooks"] = bounds_hook

            result = Runner.run_sync(
                self.agent,
                input=input_messages,
                context=context,
                max_turns=max_turns or MAX_AGENT_TURNS,
                run_config=self._run_config(user),
                **run_kwargs,
            )

            response_content = result.final_output or ""
            metadata = extract_run_metadata(result)
            usage = extract_usage(result, model or self.model)

            # Add assistant message (with run metadata) to conversation
            self.add_assistant_message(
                conversation,
                response_content,
                build_message_metadata(
                    tool_calls=extract_tool_call_records(result),
                    files_changed=metadata["files_changed"],
                    plan=list(context.plan),
                    usage=usage,
                    dispatched_tasks=dispatch_task_refs(context.dispatched_tasks),
                ),
            )
            self._finalize_task_run(conversation, context, response_content)
            self._record_usage_event(user, model, usage, conversation)

            result_payload = {
                "success": True,
                "response": response_content,
                "conversation_id": conversation.id,
                "files_changed": metadata["files_changed"],
                "tool_calls": metadata["tool_calls"],
                "plan": context.plan,
                "single_message": True,
            }
            if context.dispatched_tasks:
                result_payload["dispatched_tasks"] = list(context.dispatched_tasks)
            return result_payload

        except (MaxTurnsExceeded, RunBudgetExceeded, RunDeadlineExceeded) as cap:
            # The run hit one of its caps (turns, cost, or wall clock).
            # Everything the agent wrote before the cap is already on disk, so
            # surface a partial (capped) result rather than a hard failure. The
            # SDK result object is lost here, so the files it produced are read
            # back off the working tree instead.
            logger.info("Agent run capped for conversation %s: %s",
                        conversation.id if conversation else None, cap)
            files_changed = self._capped_run_files(conversation)
            capped_note = _capped_run_note(files_changed)
            if conversation is not None:
                try:
                    self.add_assistant_message(
                        conversation,
                        capped_note,
                        build_message_metadata(
                            files_changed=files_changed,
                            plan=list(getattr(context, "plan", []) or []),
                        ),
                    )
                except Exception:  # pragma: no cover - best effort persistence
                    logger.warning("Could not persist capped-run note", exc_info=True)
                # A capped run is a finished run: its files are on disk, so it
                # routes back to the main thread like any other. Without this a
                # capped task would sit at 'active' forever — never applied,
                # never reviewed, and never reported to the user.
                self._finalize_task_run(conversation, context, capped_note)
            return {
                "success": True,
                "capped": True,
                "response": capped_note,
                "conversation_id": conversation.id if conversation else None,
                "files_changed": files_changed,
                "tool_calls": [],
                "plan": list(getattr(context, "plan", []) or []),
            }

        except Exception as e:
            logger.error(f"Error in imagi_agent run: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            if conversation is not None:
                self._file_check_in(
                    conversation, 'error', f"The task hit an error: {str(e)[:500]}"
                )
            return {
                "success": False,
                "error": str(e),
                "conversation_id": conversation.id if conversation else None,
            }
        finally:
            # _prepare_run marked the run in flight; the blocking path ends
            # here (the holder covers a raise between its commit and return).
            if conversation is None:
                conversation = run_state.get("conversation")
            if conversation is not None:
                self._clear_run_started(conversation)
