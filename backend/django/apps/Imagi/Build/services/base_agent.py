"""
Base Agent Service using OpenAI Agents SDK.

This module provides the agent harness for the Imagi workspace: it owns
conversation persistence, context construction (including automatic history
compaction), the agent run loop, and extraction of structured run metadata
(plan, tool calls, changed files) for the workspace UI.
"""

import json
import os
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
DEFAULT_MODEL = _BUILDER_SETTINGS.get('DEFAULT_MODEL', 'gpt-5.6-sol')

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


def build_message_metadata(
    tool_calls: Optional[List[Dict[str, Any]]] = None,
    files_changed: Optional[List[str]] = None,
    plan: Optional[List[Dict[str, str]]] = None,
    usage: Optional[Dict[str, Any]] = None,
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
    return metadata or None


@dataclass
class AgentContext:
    """Context object passed to all agents during a run."""
    user_id: int
    project_id: Optional[int] = None
    project_name: Optional[str] = None
    project_description: Optional[str] = None
    project_path: Optional[str] = None
    conversation_id: Optional[int] = None
    current_file: Optional[Dict[str, Any]] = None
    # Working plan maintained by the agent via the update_plan tool
    plan: List[Dict[str, str]] = field(default_factory=list)


class ImagiAgentService:
    """
    Agent service for the Imagi workspace using OpenAI Agents SDK.

    A single agent (the Imagi agent) handles everything — conversation and
    file editing alike. This service owns conversation persistence, context
    construction, and the run loop around that agent.
    """

    def __init__(self, model: str = DEFAULT_MODEL, reasoning_effort: Optional[str] = None):
        """
        Initialize the agent service.

        Args:
            model: The OpenAI model to use (default: gpt-5.6-sol)
            reasoning_effort: How much reasoning the model should use
                ('low', 'medium', 'high'). None uses the model default.
        """
        self.model = model
        self.reasoning_effort = reasoning_effort
        self._agent = None

        # Verify API key is available
        if not OPENAI_API_KEY:
            logger.warning("OpenAI API key not found - agent features may not work properly")
        else:
            # Set environment variable for the agents SDK
            os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

    def _apply_reasoning_effort(self, reasoning_effort: Optional[str]) -> None:
        """Update the reasoning effort, invalidating the cached agent if it changed."""
        if reasoning_effort is not None and reasoning_effort != self.reasoning_effort:
            self.reasoning_effort = reasoning_effort
            self._agent = None

    @property
    def agent(self) -> Agent:
        """Lazy-load the Imagi agent."""
        if self._agent is None:
            from .coding_agent import create_coding_agent
            self._agent = create_coding_agent(self.model, self.reasoning_effort)
        return self._agent

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
    ) -> AgentConversation:
        """Create a new conversation."""
        from .coding_agent import CODING_AGENT_INSTRUCTIONS

        conversation = AgentConversation.objects.create(
            user=user,
            model_name=model,
            project_id=project_id,
            mode="agent",
            title=title,
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
        # before the checkpoint below can snapshot it)
        project_info = self.get_project_info(project_id, user)

        # Checkpoint: capture the project state this message starts from, so
        # the workspace can offer a per-message restore point (conversation
        # and files rewind together). Best-effort — a checkpoint failure must
        # never block the run itself.
        user_message_metadata = None
        if project_info.get("project_path"):
            try:
                from .version_control_service import VersionControlService
                checkpoint = VersionControlService().ensure_checkpoint(
                    project_info["project_path"],
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
            conversation_id=conversation.id,
            current_file=current_file,
        )

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
        conversation.run_started_at = timezone.now()
        conversation.save(update_fields=["run_started_at"])

        return conversation, context, input_messages

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
                ),
            )
            persisted = True

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
            yield done_event

        except MaxTurnsExceeded:
            # The run was cut off by the turn cap, not a real failure: the
            # code:'max_turns' lets the frontend offer a "Continue" action
            # (the finally block below keeps the partial reply).
            logger.warning(f"Agent run hit the turn limit ({MAX_AGENT_TURNS} turns)")
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
                        )
                        await sync_to_async(self.add_assistant_message)(
                            conversation, partial, partial_metadata
                        )
                    except Exception as e:  # pragma: no cover - best effort
                        logger.warning(f"Could not persist partial agent reply: {e}")
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
    ) -> Dict[str, Any]:
        """
        Process a message with the Imagi agent.

        The agent both chats and edits project files, deciding on its own when
        to use tools. Persists the message, builds context and (compacted)
        history, runs the agent, and returns the response plus run metadata:
        the files it changed, the tools it called, and its working plan.
        """
        if not project_id:
            return {"success": False, "error": "Project ID is required"}

        conversation = None
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

            result = Runner.run_sync(
                self.agent,
                input=input_messages,
                context=context,
                max_turns=MAX_AGENT_TURNS,
                run_config=self._run_config(user),
            )

            response_content = result.final_output or ""
            metadata = extract_run_metadata(result)

            # Add assistant message (with run metadata) to conversation
            self.add_assistant_message(
                conversation,
                response_content,
                build_message_metadata(
                    tool_calls=extract_tool_call_records(result),
                    files_changed=metadata["files_changed"],
                    plan=list(context.plan),
                    usage=extract_usage(result, model or self.model),
                ),
            )

            return {
                "success": True,
                "response": response_content,
                "conversation_id": conversation.id,
                "files_changed": metadata["files_changed"],
                "tool_calls": metadata["tool_calls"],
                "plan": context.plan,
                "single_message": True,
            }

        except Exception as e:
            logger.error(f"Error in imagi_agent run: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
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


# Singleton instance
_agent_service_instance: Optional[ImagiAgentService] = None


def get_agent_service(model: str = DEFAULT_MODEL) -> ImagiAgentService:
    """Get or create the singleton agent service instance."""
    global _agent_service_instance
    if _agent_service_instance is None or _agent_service_instance.model != model:
        _agent_service_instance = ImagiAgentService(model=model)
    return _agent_service_instance
