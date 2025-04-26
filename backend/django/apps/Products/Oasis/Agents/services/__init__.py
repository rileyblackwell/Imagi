"""
Imagi Oasis Agent Services

This package provides agent services for AI-powered chatbots and assistants.
"""

from .agent_service import (
    BaseAgentService,
    build_conversation_history,
    format_system_prompt,
    get_conversation_summary,
)
from .model_definitions import MODEL_COSTS
from .template_agent_service import TemplateAgentService
from .stylesheet_agent_service import StylesheetAgentService
from .chat_agent_service import ChatAgentService

# Backward compatibility adapter functions
def process_builder_mode_input(*args, **kwargs):
    """Adapter for process_builder_mode_input that delegates to BaseAgentService."""
    service = BaseAgentService()
    if hasattr(service, 'process_builder_mode_input'):
        return service.process_builder_mode_input(*args, **kwargs)
    return {"success": False, "error": "Service not implemented"}

def process_chat_mode_input(*args, **kwargs):
    """Adapter for process_chat_mode_input that delegates to ChatAgentService."""
    service = ChatAgentService()
    if hasattr(service, 'process_message'):
        return service.process_message(*args, **kwargs)
    return {"success": False, "error": "Service not implemented"}

def check_user_credits(user, model):
    """Adapter for check_user_credits that delegates to BaseAgentService."""
    service = BaseAgentService()
    return service.check_user_credits(user, model)

def deduct_credits(user, model):
    """Adapter for deduct_credits that delegates to BaseAgentService."""
    service = BaseAgentService()
    return service.deduct_credits(user, model)

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

__all__ = [
    # Base agent service
    'BaseAgentService',
    
    # Specialized agent services
    'ChatAgentService',
    'TemplateAgentService',
    'StylesheetAgentService',
    
    # Utility functions
    'build_conversation_history',
    'get_conversation_summary',
    'format_system_prompt',
    
    # Constants
    'MODEL_COSTS',
    
    # Backward compatibility functions
    'process_builder_mode_input',
    'process_chat_mode_input',
    'check_user_credits',
    'deduct_credits',
    'get_active_conversation',
    'undo_last_action_service'
] 