"""
Base Agent Service using OpenAI Agents SDK.

This module provides the main orchestrator agent for the Imagi workspace.
It manages handoffs to specialized sub-agents based on the user's request.
"""

import os
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from dotenv import load_dotenv

from agents import Agent, Runner, handoff, RunConfig
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
DEFAULT_MODEL = "gpt-5.2"


@dataclass
class AgentContext:
    """Context object passed to all agents during a run."""
    user_id: int
    project_id: Optional[int] = None
    project_name: Optional[str] = None
    project_description: Optional[str] = None
    conversation_id: Optional[int] = None
    current_file: Optional[Dict[str, Any]] = None
    mode: str = "chat"


class ImagiAgentService:
    """
    Main agent service for the Imagi workspace using OpenAI Agents SDK.
    
    This service handles:
    - Agent orchestration and handoffs
    - Conversation persistence
    - Integration with Django models
    """
    
    def __init__(self, model: str = DEFAULT_MODEL):
        """
        Initialize the agent service.
        
        Args:
            model: The OpenAI model to use (default: gpt-5.2)
        """
        self.model = model
        self._chat_agent = None
        self._orchestrator_agent = None
        
        # Verify API key is available
        if not OPENAI_API_KEY:
            logger.warning("OpenAI API key not found - agent features may not work properly")
        else:
            # Set environment variable for the agents SDK
            os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
    
    @property
    def chat_agent(self) -> Agent:
        """Lazy-load the chat agent."""
        if self._chat_agent is None:
            from .chat_agent import create_chat_agent
            self._chat_agent = create_chat_agent(self.model)
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
        
        return Agent[AgentContext](
            name="Imagi Orchestrator",
            instructions=instructions,
            model=self.model,
            handoffs=[
                handoff(
                    agent=self.chat_agent,
                    tool_description="Hand off to the chat agent for general conversations, "
                                     "questions, explanations, and guidance about web development."
                )
            ]
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
        project_id: Optional[int] = None
    ) -> AgentConversation:
        """Create a new conversation."""
        from .chat_agent import CHAT_AGENT_INSTRUCTIONS
        
        conversation = AgentConversation.objects.create(
            user=user,
            model_name=model,
            project_id=project_id
        )
        
        prompt_content = system_prompt or CHAT_AGENT_INSTRUCTIONS
        SystemPrompt.objects.create(
            conversation=conversation,
            content=prompt_content
        )
        
        return conversation
    
    def add_user_message(self, conversation: AgentConversation, content: str) -> AgentMessage:
        """Add a user message to the conversation."""
        return AgentMessage.objects.create(
            conversation=conversation,
            role="user",
            content=content
        )
    
    def add_assistant_message(self, conversation: AgentConversation, content: str) -> AgentMessage:
        """Add an assistant message to the conversation."""
        return AgentMessage.objects.create(
            conversation=conversation,
            role="assistant",
            content=content
        )
    
    def build_conversation_history(self, conversation: AgentConversation) -> List[Dict[str, str]]:
        """Build conversation history for the agent."""
        messages = []
        
        history_messages = AgentMessage.objects.filter(
            conversation=conversation
        ).order_by('created_at')
        
        for msg in history_messages:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        return messages
    
    def get_project_info(self, project_id: Optional[int], user) -> Dict[str, Any]:
        """Get project information."""
        project_info = {
            "project_id": project_id,
            "project_name": None,
            "project_description": None,
        }
        
        if not project_id:
            return project_info
        
        try:
            from apps.Products.Imagi.ProjectManager.models import Project
            project = Project.objects.get(id=project_id, user=user)
            project_info["project_name"] = project.name
            project_info["project_description"] = getattr(project, 'description', None)
        except Exception as e:
            logger.warning(f"Could not get project info: {e}")
        
        return project_info
    
    # -------------------------------------------------------------------------
    # Main Chat Processing
    # -------------------------------------------------------------------------
    
    def process_chat(
        self,
        user_input: str,
        user,
        model: Optional[str] = None,
        project_id: Optional[int] = None,
        current_file: Optional[Dict[str, Any]] = None,
        conversation_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Process a chat message using the OpenAI Agents SDK.
        
        Args:
            user_input: The user's message
            user: The Django user object
            model: The AI model to use (defaults to self.model)
            project_id: Optional project ID
            current_file: Optional current file context
            conversation_id: Optional existing conversation ID
            
        Returns:
            Dict containing the response and metadata
        """
        try:
            # Validate input
            if not user_input:
                return {"success": False, "error": "Message is required"}
            
            model = model or self.model
            
            # Get or create conversation
            if conversation_id:
                conversation = self.get_conversation(conversation_id, user)
                if not conversation:
                    conversation = self.create_conversation(user, model, project_id=project_id)
            else:
                conversation = self.create_conversation(user, model, project_id=project_id)
            
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
                conversation_id=conversation.id,
                current_file=current_file,
                mode="chat"
            )
            
            # Build conversation history (excluding the current message we just added)
            conversation_history = self.build_conversation_history(conversation)
            if conversation_history and conversation_history[-1]["role"] == "user":
                conversation_history = conversation_history[:-1]
            
            # Build input for the agent
            input_messages = []
            if conversation_history:
                input_messages.extend(conversation_history)
            input_messages.append({"role": "user", "content": user_input})
            
            # Run the chat agent directly (skip orchestrator for now)
            result = Runner.run_sync(
                self.chat_agent,
                input=input_messages,
                context=context,
                run_config=RunConfig(
                    workflow_name="imagi_chat",
                    trace_metadata={"user_id": user.id}
                )
            )
            
            response_content = result.final_output or ""
            
            # Add assistant message to conversation
            self.add_assistant_message(conversation, response_content)
            
            return {
                "success": True,
                "response": response_content,
                "conversation_id": conversation.id,
                "single_message": True,
            }
            
        except Exception as e:
            logger.error(f"Error in process_chat: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e),
                "conversation_id": conversation.id if 'conversation' in locals() else None
            }


# Singleton instance
_agent_service_instance: Optional[ImagiAgentService] = None


def get_agent_service(model: str = DEFAULT_MODEL) -> ImagiAgentService:
    """Get or create the singleton agent service instance."""
    global _agent_service_instance
    if _agent_service_instance is None or _agent_service_instance.model != model:
        _agent_service_instance = ImagiAgentService(model=model)
    return _agent_service_instance
