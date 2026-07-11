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
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from dotenv import load_dotenv

from agents import Agent, Runner, handoff, RunConfig

try:  # ModelSettings location can vary across SDK versions
    from agents import ModelSettings
except ImportError:  # pragma: no cover - defensive fallback
    ModelSettings = None

try:  # Reasoning config for the OpenAI Responses API
    from openai.types.shared import Reasoning
except ImportError:  # pragma: no cover - defensive fallback
    Reasoning = None

from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

from django.conf import settings
from django.shortcuts import get_object_or_404

from ..models import AgentConversation, AgentMessage, SystemPrompt

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Get API key
OPENAI_API_KEY = os.getenv('OPENAI_KEY') or getattr(settings, 'OPENAI_KEY', None)

# Default model for agents
DEFAULT_MODEL = "gpt-5.6-sol"

# Upper bound on agent-loop iterations for a single request. Chat mode has no
# tools so it resolves in one turn; agent mode gets room for plan → search →
# read → edit → verify cycles without letting a confused run spin forever.
MAX_CHAT_TURNS = 6
MAX_AGENT_TURNS = 30

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
    mode: str = "chat"
    # Working plan maintained by the agent via the update_plan tool
    plan: List[Dict[str, str]] = field(default_factory=list)


class ImagiAgentService:
    """
    Main agent service for the Imagi workspace using OpenAI Agents SDK.

    This service handles:
    - Agent orchestration and handoffs
    - Conversation persistence
    - Integration with Django models
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
        self._chat_agent = None
        self._coding_agent = None
        self._orchestrator_agent = None

        # Verify API key is available
        if not OPENAI_API_KEY:
            logger.warning("OpenAI API key not found - agent features may not work properly")
        else:
            # Set environment variable for the agents SDK
            os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

    def _apply_reasoning_effort(self, reasoning_effort: Optional[str]) -> None:
        """Update the reasoning effort, invalidating cached agents if it changed."""
        if reasoning_effort is not None and reasoning_effort != self.reasoning_effort:
            self.reasoning_effort = reasoning_effort
            self._chat_agent = None
            self._coding_agent = None
            self._orchestrator_agent = None

    @property
    def coding_agent(self) -> Agent:
        """Lazy-load the coding agent."""
        if self._coding_agent is None:
            from .coding_agent import create_coding_agent
            self._coding_agent = create_coding_agent(self.model, self.reasoning_effort)
        return self._coding_agent

    @property
    def chat_agent(self) -> Agent:
        """Lazy-load the chat agent."""
        if self._chat_agent is None:
            from .chat_agent import create_chat_agent
            self._chat_agent = create_chat_agent(self.model, self.reasoning_effort)
        return self._chat_agent

    @property
    def orchestrator_agent(self) -> Agent:
        """
        Get or create the main orchestrator agent.

        The orchestrator can hand off to specialized sub-agents.
        """
        if self._orchestrator_agent is None:
            self._orchestrator_agent = self._create_orchestrator_agent()
        return self._orchestrator_agent

    def _create_orchestrator_agent(self) -> Agent:
        """Create the main orchestrator agent with handoffs."""
        instructions = f"""{RECOMMENDED_PROMPT_PREFIX}

You are Imagi, an AI-powered web development assistant. You help users build,
understand, and improve their web applications.

Your capabilities include:
1. **Chat Mode**: Have natural conversations about web development, explain concepts,
   answer questions, and provide guidance on best practices.
2. **Build Mode** (coming soon): Generate and modify code for Vue.js components,
   Django templates, and other web development artifacts.

Current Behavior:
- When the user wants to chat, discuss code, or ask questions, use the chat agent.
- Be helpful, concise, and provide practical advice.
- Remember that users may have varying levels of technical expertise.

Technology Stack:
- Backend: Django with REST framework
- Frontend: Vue.js 3 with Composition API
- Styling: TailwindCSS
- Build tools: Vite
- State management: Pinia
- HTTP client: Axios
"""

        from apps.Imagi.Build.Builder.services.models_service import (
            get_backend_model_id,
            get_model_identity_instructions,
        )
        instructions += "\n\n" + get_model_identity_instructions(self.model)
        backend_model = get_backend_model_id(self.model)
        kwargs = {}
        settings = build_model_settings(self.reasoning_effort)
        if settings is not None:
            kwargs['model_settings'] = settings
        return Agent[AgentContext](
            name="Imagi Orchestrator",
            instructions=instructions,
            model=backend_model,
            handoffs=[
                handoff(
                    agent=self.chat_agent,
                    tool_description="Hand off to the chat agent for general conversations, "
                                     "questions, explanations, and guidance about web development."
                )
            ],
            **kwargs
        )

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
        mode: str = "chat",
        title: str = "",
    ) -> AgentConversation:
        """Create a new conversation."""
        from .chat_agent import CHAT_AGENT_INSTRUCTIONS

        conversation = AgentConversation.objects.create(
            user=user,
            model_name=model,
            project_id=project_id,
            mode=mode,
            title=title,
        )

        prompt_content = system_prompt or CHAT_AGENT_INSTRUCTIONS
        SystemPrompt.objects.create(
            conversation=conversation,
            content=prompt_content
        )

        return conversation

    def add_user_message(self, conversation: AgentConversation, content: str) -> AgentMessage:
        """Add a user message to the conversation."""
        message = AgentMessage.objects.create(
            conversation=conversation,
            role="user",
            content=content
        )
        if not conversation.title:
            conversation.title = (content or "").strip().splitlines()[0][:80]
            conversation.save(update_fields=["title", "updated_at"])
        else:
            conversation.save(update_fields=["updated_at"])
        return message

    def add_assistant_message(self, conversation: AgentConversation, content: str) -> AgentMessage:
        """Add an assistant message to the conversation."""
        return AgentMessage.objects.create(
            conversation=conversation,
            role="assistant",
            content=content
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
            from apps.Imagi.Build.ProjectManager.models import Project
            project = Project.objects.get(id=project_id, user=user)
            project_info["project_name"] = project.name
            project_info["project_description"] = getattr(project, 'description', None)
            project_info["project_path"] = getattr(project, 'project_path', None)
        except Exception as e:
            logger.warning(f"Could not get project info: {e}")

        return project_info

    # -------------------------------------------------------------------------
    # Main Processing
    # -------------------------------------------------------------------------

    def _run(
        self,
        agent: Agent,
        mode: str,
        workflow_name: str,
        max_turns: int,
        user_input: str,
        user,
        model: Optional[str] = None,
        project_id: Optional[int] = None,
        current_file: Optional[Dict[str, Any]] = None,
        conversation_id: Optional[int] = None,
        reasoning_effort: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Shared harness core: persist the message, build context and history,
        run the agent, and persist + return the structured result."""
        conversation = None
        try:
            if not user_input:
                return {"success": False, "error": "Message is required"}

            model = model or self.model
            self._apply_reasoning_effort(reasoning_effort)

            # Get or create conversation
            if conversation_id:
                conversation = self.get_conversation(conversation_id, user)
            if conversation is None:
                conversation = self.create_conversation(
                    user, model, project_id=project_id, mode=mode
                )

            # Add user message to conversation
            self.add_user_message(conversation, user_input)

            # Get project info
            project_info = self.get_project_info(project_id, user)

            # Build context for the agent
            context = AgentContext(
                user_id=user.id,
                project_id=project_id,
                project_name=project_info["project_name"],
                project_description=project_info["project_description"],
                project_path=project_info["project_path"],
                conversation_id=conversation.id,
                current_file=current_file,
                mode=mode,
            )

            # Build (compacted) conversation history, excluding the message we
            # just persisted — it is appended as the current input below.
            conversation_history = self.build_conversation_history(conversation)
            if conversation_history and conversation_history[-1]["role"] == "user" \
                    and conversation_history[-1]["content"] == user_input:
                conversation_history = conversation_history[:-1]

            input_messages = list(conversation_history)
            input_messages.append({"role": "user", "content": user_input})

            result = Runner.run_sync(
                agent,
                input=input_messages,
                context=context,
                max_turns=max_turns,
                run_config=RunConfig(
                    workflow_name=workflow_name,
                    trace_metadata={"user_id": str(user.id)}
                )
            )

            response_content = result.final_output or ""
            metadata = extract_run_metadata(result)

            # Add assistant message to conversation
            self.add_assistant_message(conversation, response_content)

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
            logger.error(f"Error in {workflow_name}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e),
                "conversation_id": conversation.id if conversation else None,
            }

    def process_chat(
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
        Process a chat message using the chat agent (no file tools).

        Returns a dict containing the response and metadata.
        """
        return self._run(
            agent=self.chat_agent,
            mode="chat",
            workflow_name="imagi_chat",
            max_turns=MAX_CHAT_TURNS,
            user_input=user_input,
            user=user,
            model=model,
            project_id=project_id,
            current_file=current_file,
            conversation_id=conversation_id,
            reasoning_effort=reasoning_effort,
        )

    def process_agent(
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
        Process a message using the Coding Agent (agent mode).

        The coding agent can both chat and edit project files using function
        tools. Returns the response plus run metadata: the files it changed,
        the tools it called, and its working plan.
        """
        if not project_id:
            return {"success": False, "error": "Project ID is required for agent mode"}

        return self._run(
            agent=self.coding_agent,
            mode="agent",
            workflow_name="imagi_agent",
            max_turns=MAX_AGENT_TURNS,
            user_input=user_input,
            user=user,
            model=model,
            project_id=project_id,
            current_file=current_file,
            conversation_id=conversation_id,
            reasoning_effort=reasoning_effort,
        )


# Singleton instance
_agent_service_instance: Optional[ImagiAgentService] = None


def get_agent_service(model: str = DEFAULT_MODEL) -> ImagiAgentService:
    """Get or create the singleton agent service instance."""
    global _agent_service_instance
    if _agent_service_instance is None or _agent_service_instance.model != model:
        _agent_service_instance = ImagiAgentService(model=model)
    return _agent_service_instance
