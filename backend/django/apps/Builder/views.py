"""
Core business logic for the Builder app.
All API endpoints are handled in the api/ directory.
"""

import os
import shutil
import logging
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from .models import Project, Conversation, Message, Page
from apps.ProjectManager.services import ProjectGenerationService

logger = logging.getLogger(__name__)

@method_decorator(never_cache, name='dispatch')
class BuilderView:
    """Base view for Builder app with cache control."""
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        # Prevent bfcache
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response

def create_project_with_conversation(user, project_name):
    """
    Creates a new project and its initial conversation.
    
    Args:
        user: The user creating the project
        project_name: Name of the project
        
    Returns:
        tuple: (project, conversation) if successful, (None, None) if failed
    """
    try:
        # Create Django project using ProjectManager service
        service = ProjectGenerationService(user)
        user_project = service.create_project(project_name)
        
        # Create the Project instance
        project = Project.objects.create(
            user=user,
            name=project_name,
            user_project=user_project
        )
        
        # Create initial conversation
        conversation = Conversation.objects.create(
            user=user,
            project=project
        )
        
        logger.info(f"Created project '{project_name}' for user {user.username}")
        return project, conversation
        
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        # Clean up if anything fails
        if user_project and os.path.exists(user_project.project_path):
            shutil.rmtree(user_project.project_path)
        if 'user_project' in locals():
            user_project.delete()
        if 'project' in locals():
            project.delete()
        return None, None

def load_project_files(project):
    """
    Load all files for a project from the database into the project's directories.
    
    Args:
        project: The Project instance to load files for
        
    Raises:
        ValueError: If no associated user project is found
    """
    if not project.user_project:
        raise ValueError("No associated user project found")
        
    project_path = project.user_project.project_path
    templates_dir = os.path.join(project_path, 'templates')
    static_css_dir = os.path.join(project_path, 'static', 'css')
    
    # Ensure directories exist
    os.makedirs(templates_dir, exist_ok=True)
    os.makedirs(static_css_dir, exist_ok=True)

    # Load all pages for this project
    pages = Page.objects.filter(
        conversation__project=project
    ).select_related('conversation')

    # For each page, get the latest content and write to file
    for page in pages:
        latest_message = Message.objects.filter(
            conversation__project=project,
            page=page,
            role='assistant'
        ).order_by('-created_at').first()
        
        if latest_message:
            if page.filename.endswith('.html'):
                output_dir = templates_dir
            elif page.filename.endswith('.css'):
                output_dir = static_css_dir
            else:
                continue  # Skip unsupported file types
                
            file_path = os.path.join(output_dir, page.filename)
            with open(file_path, 'w') as f:
                f.write(latest_message.content)

def clear_conversation_history(conversation):
    """
    Clears all messages and pages from a conversation.
    
    Args:
        conversation: The Conversation instance to clear
    """
    try:
        Message.objects.filter(conversation=conversation).delete()
        Page.objects.filter(conversation=conversation).delete()
        logger.info(f"Cleared conversation history for conversation {conversation.id}")
        return True
    except Exception as e:
        logger.error(f"Error clearing conversation history: {str(e)}")
        return False

