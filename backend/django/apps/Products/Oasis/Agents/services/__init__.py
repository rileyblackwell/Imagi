"""
Agent services module for Imagi Oasis.

This module exports the agent services classes used for AI-powered generation
and conversation capabilities in the Imagi Oasis platform.
"""

# Import base agent service
from .agent_service import BaseAgentService

# Import specialized agent services
from .template_agent_service import TemplateAgentService
from .chat_agent_service import ChatAgentService

# Import the agent factory
from .agent_factory import AgentFactory

# Try to import StylesheetAgentService if it exists
try:
    from .stylesheet_agent_service import StylesheetAgentService
    has_stylesheet_service = True
except ImportError:
    has_stylesheet_service = False

# Utility functions from agent_service.py
from .agent_service import build_conversation_history, format_system_prompt, get_conversation_summary

try:
    from apps.Products.Oasis.Builder.services.models_service import MODEL_COSTS
except ImportError:
    MODEL_COSTS = {}  # Provide fallback empty dict if import fails

# Backward compatibility adapter functions
def process_builder_mode_input(user_input, model, file_path, user, project_id=None, conversation_id=None):
    """
    Adapter for process_builder_mode_input that delegates to TemplateAgentService.
    
    Args:
        user_input (str): The user's prompt
        model (str): The AI model to use
        file_path (str): The file path being edited
        user: The Django user object
        project_id (str, optional): The project ID
        conversation_id (int, optional): Existing conversation ID
        
    Returns:
        dict: The result of the operation
    """
    service = TemplateAgentService()
    return service.process_template(
        prompt=user_input,
        model=model,
        user=user,
        project_id=project_id,
        file_name=file_path,
        conversation_id=conversation_id
    )

def process_chat_mode_input(*args, **kwargs):
    """Adapter for process_chat_mode_input that delegates to ChatAgentService."""
    service = ChatAgentService()
    return service.process_message(*args, **kwargs)

def check_user_credits(user, model):
    """Adapter for check_user_credits that delegates to BaseAgentService."""
    service = BaseAgentService()
    return service.check_user_credits(user, model)

def deduct_credits(user, model, completion_tokens=None):
    """
    Adapter for deduct_credits that delegates to BaseAgentService.
    
    Args:
        user: The Django user object
        model (str): The model ID
        completion_tokens (int, optional): The number of completion tokens
        
    Returns:
        float: The amount of credits deducted
    """
    service = BaseAgentService()
    # BaseAgentService.deduct_credits expects a user ID, not a user object
    return service.deduct_credits(user.id, model, completion_tokens)

def get_active_conversation(user):
    """
    Adapter for the deprecated get_active_conversation function.
    Returns the most recent conversation for the user.
    """
    from ..models import AgentConversation
    conversation = AgentConversation.objects.filter(
        user=user
    ).order_by('-created_at').first()
    
    if not conversation:
        raise ValueError('No active conversation found for this user.')
    
    return conversation

def undo_last_action_service(*args, **kwargs):
    """
    Adapter for undo_last_action_service.
    Delegates to the Undo Service in the Builder app if available.
    """
    try:
        from apps.Products.Oasis.Builder.services.undo_service import UndoService
        undo_service = UndoService()
        return undo_service.undo_agent_message(*args, **kwargs)
    except ImportError:
        return {"success": False, "error": "Undo service not available"}
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in undo_last_action_service: {str(e)}")
        return {"success": False, "error": str(e)}

# Construct exports list based on available services
exports = [
    'BaseAgentService',
    'TemplateAgentService',
    'ChatAgentService',
    'AgentFactory',
    'build_conversation_history',
    'format_system_prompt',
    'get_conversation_summary',
    # Backward compatibility exports
    'process_builder_mode_input',
    'process_chat_mode_input',
    'check_user_credits',
    'deduct_credits',
    'get_active_conversation',
    'undo_last_action_service',
    'MODEL_COSTS'
]

# Add StylesheetAgentService to exports if available
if has_stylesheet_service:
    exports.append('StylesheetAgentService')

# Export all agent services and functions
__all__ = exports 