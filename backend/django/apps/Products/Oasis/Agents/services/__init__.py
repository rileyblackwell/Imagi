"""
Agent services module for Imagi Oasis.

This module provides specialized AI agent services for different types of content generation:
- ChatAgentService: For natural language chat interactions
- TemplateAgentService: For Django HTML template generation
- StylesheetAgentService: For CSS stylesheet generation
"""

# Export only the concrete agent services, not the base class
from .chat_agent_service import ChatAgentService
from .template_agent_service import TemplateAgentService
from .stylesheet_agent_service import StylesheetAgentService

# Export utility functions that might be needed by views
from .agent_service import build_conversation_history, get_conversation_summary

__all__ = [
    'ChatAgentService',
    'TemplateAgentService',
    'StylesheetAgentService',
    'build_conversation_history',
    'get_conversation_summary'
] 