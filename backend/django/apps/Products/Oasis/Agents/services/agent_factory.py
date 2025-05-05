"""
Agent factory module for Imagi Oasis.

This module provides a factory for creating agent service instances based on different
modes, file types, or service requirements.
"""

import logging
from .chat_agent_service import ChatAgentService
from .template_agent_service import TemplateAgentService

# Configure logging
logger = logging.getLogger(__name__)

class AgentFactory:
    """
    Factory for creating appropriate agent service instances.
    
    This class provides methods to create the appropriate agent service based on
    the mode, file type, or specific requirements of the request.
    """
    
    @staticmethod
    def get_agent_for_mode(mode):
        """
        Get the appropriate agent service for a given mode.
        
        Args:
            mode (str): The interaction mode ('chat', 'build', 'template', etc.)
            
        Returns:
            BaseAgentService: An instance of the appropriate agent service
        """
        if mode == 'build' or mode == 'template':
            return TemplateAgentService()
        else:  # Default to chat mode
            return ChatAgentService()
    
    @staticmethod
    def get_agent_for_file_type(file_path):
        """
        Get the appropriate agent service based on file extension.
        
        Args:
            file_path (str): The path to the file
            
        Returns:
            BaseAgentService: An instance of the appropriate agent service
        """
        if not file_path:
            return ChatAgentService()
            
        file_path = file_path.lower()
        
        # HTML files should use TemplateAgentService
        if file_path.endswith('.html'):
            return TemplateAgentService()
        # CSS files should use StylesheetAgentService (if available)
        elif file_path.endswith('.css'):
            try:
                from .stylesheet_agent_service import StylesheetAgentService
                return StylesheetAgentService()
            except ImportError:
                logger.warning("StylesheetAgentService not available, using ChatAgentService")
                return ChatAgentService()
        # All other file types use ChatAgentService
        else:
            return ChatAgentService()
    
    @staticmethod
    def get_agent_for_request(request_data):
        """
        Analyze request data and return the most appropriate agent service.
        
        Args:
            request_data (dict): The request data containing mode, file_path, etc.
            
        Returns:
            BaseAgentService: An instance of the appropriate agent service
        """
        # Extract relevant information from request_data
        mode = request_data.get('mode')
        file_path = None
        
        # Try different key names for file path
        if 'file_path' in request_data:
            file_path = request_data['file_path']
        elif 'file' in request_data and isinstance(request_data['file'], dict):
            file_path = request_data['file'].get('path')
        
        # First check mode, as it takes precedence
        if mode:
            return AgentFactory.get_agent_for_mode(mode)
        
        # If no mode specified, check file type
        if file_path:
            return AgentFactory.get_agent_for_file_type(file_path)
        
        # Default to chat agent if no specific criteria
        return ChatAgentService() 