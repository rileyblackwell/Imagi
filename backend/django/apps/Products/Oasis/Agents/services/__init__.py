"""
Agent services module for Imagi Oasis.

This module provides specialized AI agent services for different types of content generation:
- ChatAgentService: For natural language chat interactions
- TemplateAgentService: For Django HTML template generation
- StylesheetAgentService: For CSS stylesheet generation
"""

# Export the base agent service for extension
from .agent_service import BaseAgentService

# Export the specialized agent services
from .chat_agent_service import ChatAgentService
from .template_agent_service import TemplateAgentService
from .stylesheet_agent_service import StylesheetAgentService

# Export utility functions that might be needed by views
from .agent_service import build_conversation_history, get_conversation_summary

# Define placeholder functions that were previously imported from oasis_service
def process_builder_mode_input(*args, **kwargs):
    """Placeholder for process_builder_mode_input function."""
    return {"success": False, "error": "Service not implemented"}

def process_chat_mode_input(*args, **kwargs):
    """Placeholder for process_chat_mode_input function."""
    return {"success": False, "error": "Service not implemented"}

def check_user_credits(*args, **kwargs):
    """Placeholder for check_user_credits function."""
    return True

def deduct_credits(*args, **kwargs):
    """Placeholder for deduct_credits function."""
    return True

def get_active_conversation(*args, **kwargs):
    """Placeholder for get_active_conversation function."""
    return None

def undo_last_action_service(*args, **kwargs):
    """Placeholder for undo_last_action_service function."""
    return {"success": False, "error": "Service not implemented"}

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
    
    # Oasis service functions
    'process_builder_mode_input',
    'process_chat_mode_input',
    'check_user_credits',
    'deduct_credits',
    'get_active_conversation',
    'undo_last_action_service'
] 