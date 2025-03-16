"""
Service for project preview operations in the Builder app.
"""

import logging
from .dev_server_service import DevServerManager

logger = logging.getLogger(__name__)

class PreviewService:
    """Service for project preview operations."""
    
    def __init__(self, project):
        self.project = project
        self.dev_server = DevServerManager(project)
    
    def start_preview(self):
        """Start a development server for the project."""
        try:
            server_url = self.dev_server.get_server_url()
            
            return {
                'success': True,
                'preview_url': server_url,
                'message': 'Development server started successfully'
            }
        except Exception as e:
            logger.error(f"Error starting preview server: {str(e)}")
            raise
    
    def stop_preview(self):
        """Stop the development server."""
        try:
            self.dev_server.stop_server()
            
            return {
                'success': True,
                'message': 'Development server stopped successfully'
            }
        except Exception as e:
            logger.error(f"Error stopping preview server: {str(e)}")
            raise 