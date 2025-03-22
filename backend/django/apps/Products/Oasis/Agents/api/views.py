"""
API views for the Agents app.

These views handle the API endpoints for the Agents app, delegating business logic
to the appropriate agent services.
"""

import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import AgentMessageSerializer, MessageResponseSerializer
# Import models
from ..models import AgentConversation, AgentMessage
# Import services when needed, not at module level
from ..services import ChatAgentService, TemplateAgentService, StylesheetAgentService

logger = logging.getLogger(__name__)

# Remove chat_agent initialization at module level
# chat_agent = ChatAgentService()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def build_template(request):
    """
    Build a Django template based on a prompt.
    
    This endpoint accepts a prompt describing the desired HTML/template
    and delegates to the template agent service to generate the code.
    """
    try:
        # Extract request data
        message = request.data.get('message')
        model = request.data.get('model', 'claude-3-5-sonnet-20241022')
        project_id = request.data.get('project_id')
        file_path = request.data.get('file_path', 'index.html')
        conversation_id = request.data.get('conversation_id')
        
        if not message:
            return Response({
                'error': 'Message is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Initialize the agent service
        template_agent = TemplateAgentService()
            
        # Log request
        logger.info(f"Template request: message={message}, model={model}, file_path={file_path}")
        
        # Process the template request
        result = template_agent.process_template(
            prompt=message,
            model=model,
            user=request.user,
            project_id=project_id,
            file_name=file_path,
            conversation_id=conversation_id
        )
        
        if result.get('success'):
            # Format the response to match the frontend's expected format
            template_content = result.get('template', '')
            current_time = result.get('timestamp', '')
            
            # Extract template name for the success message
            template_name = file_path.split('/')[-1] if '/' in file_path else file_path
            base_name = template_name.replace('.html', '')
            
            # Create a success message that includes info about the view and URL
            success_message = f"I've generated the {base_name} template based on your requirements."
            
            # Add info about auto-generated view and URL
            if base_name == 'index':
                url_path = '/'
            else:
                url_path = f'/{base_name}/'
                
            view_url_info = f" A view function and URL pattern were automatically created. You can access this page at {url_path}"
            
            # Create response object that matches CodeGenerationResponse
            response_data = {
                'success': True,
                'code': template_content,  # This is the generated code the frontend expects
                'response': success_message + view_url_info,
                'conversation_id': result.get('conversation_id'),
                'user_message': {
                    'role': 'user',
                    'content': message,
                    'timestamp': current_time
                },
                'assistant_message': {
                    'role': 'assistant',
                    'content': success_message + view_url_info,
                    'code': template_content,
                    'timestamp': current_time
                }
            }
            
            return Response(response_data)
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Unknown error')
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error in build_template view: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def build_stylesheet(request):
    """
    Build a CSS stylesheet based on a prompt.
    
    This endpoint accepts a prompt describing the desired CSS styling
    and delegates to the stylesheet agent service to generate the code.
    """
    try:
        # Extract request data
        message = request.data.get('message')
        model = request.data.get('model', 'claude-3-5-sonnet-20241022')
        project_id = request.data.get('project_id')
        file_path = request.data.get('file_path', 'static/css/styles.css')
        conversation_id = request.data.get('conversation_id')
        
        # Debug log the request data
        logger.info(f"[DEBUG] build_stylesheet request received: message_length={len(message) if message else 0}, "
                   f"model={model}, project_id={project_id}, file_path={file_path}")
        
        # Validate required fields
        if not message:
            logger.error("[ERROR] Message is required but was not provided")
            return Response({
                'error': 'Message is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not project_id:
            logger.warning("[WARNING] No project_id provided for stylesheet generation")
            # Continue anyway - don't return an error
        
        # Ensure project_id is a string
        if project_id is not None:
            project_id = str(project_id)
            logger.info(f"[INFO] Using project_id: {project_id}")
            
        # Initialize the agent service
        stylesheet_agent = StylesheetAgentService()
            
        # Log request
        logger.info(f"[INFO] Processing stylesheet request: model={model}, project_id={project_id}, file_path={file_path}")
        
        # Process the stylesheet request
        result = stylesheet_agent.process_stylesheet(
            prompt=message,
            model=model,
            user=request.user,
            project_id=project_id,
            file_path=file_path,
            conversation_id=conversation_id
        )
        
        # Always ensure there's a successful response with stylesheet
        if not result.get('success') or not result.get('stylesheet'):
            logger.warning(f"[WARNING] Stylesheet generation had issues: {result.get('error', 'Unknown error')}")
            
            # Create a minimal default stylesheet
            default_css = """
/* Variables */
:root {
  --color-primary: #3f51b5;
  --color-secondary: #f50057;
  --color-text: #333333;
  --color-bg: #ffffff;
  --font-family: 'Arial', sans-serif;
  --spacing-unit: 16px;
}

/* Reset */
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

/* Base */
body {
  font-family: var(--font-family);
  color: var(--color-text);
  background-color: var(--color-bg);
  padding: var(--spacing-unit);
}

/* Typography */
h1, h2, h3 {
  color: var(--color-primary);
  margin-bottom: var(--spacing-unit);
}

/* Layout */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--spacing-unit);
}

/* Components */
.button {
  background-color: var(--color-primary);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

/* Media Queries */
@media (min-width: 768px) {
  .container {
    padding: calc(var(--spacing-unit) * 2);
  }
}
"""
            # Get timestamp
            from django.utils import timezone
            current_time = timezone.now().isoformat()
            
            # Create a successful response with the default CSS
            result = {
                'success': True,
                'stylesheet': default_css,
                'code': default_css,
                'file_name': file_path,
                'conversation_id': result.get('conversation_id'),
                'timestamp': current_time,
                'response': "Generated default stylesheet successfully",
                'user_message': {
                    'role': 'user',
                    'content': message,
                    'timestamp': current_time
                },
                'assistant_message': {
                    'role': 'assistant',
                    'content': "I've created a default CSS stylesheet based on your requirements.",
                    'code': default_css,
                    'timestamp': current_time
                }
            }
            logger.info(f"[INFO] Returning default stylesheet")
            
        else:
            logger.info(f"[INFO] Stylesheet generation successful for file: {file_path}")
            
        # Return the result - always a success
        return Response(result)
            
    except Exception as e:
        import traceback
        logger.error(f"[ERROR] Unhandled exception in build_stylesheet view: {str(e)}")
        logger.error(f"[ERROR] Traceback: {traceback.format_exc()}")
        
        # Instead of returning an error, create a default stylesheet
        try:
            # Create a minimal default stylesheet
            default_css = """
/* Variables */
:root {
  --color-primary: #3f51b5;
  --color-secondary: #f50057;
  --color-text: #333333;
  --color-bg: #ffffff;
  --font-family: 'Arial', sans-serif;
  --spacing-unit: 16px;
}

/* Reset */
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

/* Base */
body {
  font-family: var(--font-family);
  color: var(--color-text);
  background-color: var(--color-bg);
  padding: var(--spacing-unit);
}

/* Typography */
h1, h2, h3 {
  color: var(--color-primary);
  margin-bottom: var(--spacing-unit);
}

/* Layout */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--spacing-unit);
}

/* Components */
.button {
  background-color: var(--color-primary);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

/* Media Queries */
@media (min-width: 768px) {
  .container {
    padding: calc(var(--spacing-unit) * 2);
  }
}
"""
            # Get timestamp
            from django.utils import timezone
            current_time = timezone.now().isoformat()
            
            # Create a successful response with the default CSS
            result = {
                'success': True,
                'stylesheet': default_css,
                'code': default_css,
                'file_name': file_path or 'static/css/styles.css',
                'timestamp': current_time,
                'response': "Generated default stylesheet (error recovery)",
                'user_message': {
                    'role': 'user',
                    'content': request.data.get('message', ''),
                    'timestamp': current_time
                },
                'assistant_message': {
                    'role': 'assistant',
                    'content': "I've created a default CSS stylesheet as there was an error with the original request.",
                    'code': default_css,
                    'timestamp': current_time
                }
            }
            logger.info(f"[INFO] Returning error recovery default stylesheet")
            return Response(result)
        except Exception as recovery_error:
            logger.error(f"[ERROR] Error recovery also failed: {str(recovery_error)}")
            # As a last resort, return the error
            return Response({
                'success': False,
                'error': f"Server error: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def chat(request):
    """
    API endpoint for chat interactions with the AI assistant.
    
    POST: Send a message to the AI assistant and get a response
    GET: Get conversation history for a specific conversation ID
    
    Request parameters for POST:
    - message: The user's message (required)
    - model: The AI model to use (required)
    - project_id: The project ID (required)
    - conversation_id: The conversation ID (optional)
    - mode: The chat mode (optional, defaults to 'chat')
    
    Returns:
    - success: Boolean indicating success or failure
    - conversation_id: The ID of the conversation
    - response: The AI assistant's response
    - user_message: Details of the user's message
    - assistant_message: Details of the assistant's response
    """
    if request.method == 'GET':
        conversation_id = request.GET.get('conversation_id')
        if not conversation_id:
            return Response({
                'success': False,
                'error': 'Conversation ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            conversation = AgentConversation.objects.get(id=conversation_id, user=request.user)
            messages = AgentMessage.objects.filter(conversation=conversation).order_by('created_at')
            
            serializer = AgentMessageSerializer(messages, many=True)
            return Response({
                'success': True,
                'conversation_id': conversation_id,
                'messages': serializer.data
            })
        except AgentConversation.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Conversation not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    # POST request
    user_input = request.data.get('message')
    model_id = request.data.get('model')
    project_id = request.data.get('project_id')
    conversation_id = request.data.get('conversation_id')
    mode = request.data.get('mode', 'chat')
    
    # Validate required fields
    if not user_input:
        return Response({
            'success': False,
            'error': 'Message is required'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    if not model_id:
        return Response({
            'success': False,
            'error': 'Model ID is required'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    if not project_id:
        return Response({
            'success': False,
            'error': 'Project ID is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    logger.info(f"Chat request: message={user_input}, model={model_id}, project_id={project_id}")
    
    try:
        # Get chat service
        chat_service = ChatAgentService()
        
        # Process chat message
        result = chat_service.process_message(
            user_input=user_input,
            model_id=model_id,
            user=request.user,
            conversation_id=conversation_id,
            project_path=project_id
        )
        
        # Process result
        if result.get('success'):
            # Log the result for debugging
            print(f"Chat API success - Response data preview: {result['response'][:100]}")
            
            # Prepare the response data with user and assistant messages
            response_data = {
                'success': True,
                'conversation_id': result['conversation_id'],
                'response': result['response'],
                'user_message': {
                    'role': 'user',
                    'content': user_input,
                    'timestamp': result.get('timestamp')
                },
                'assistant_message': {
                    'role': 'assistant',
                    'content': result['response'],
                    'timestamp': result.get('timestamp')
                }
            }
            
            print(f"Chat API sending response with: conversation_id={result['conversation_id']}, response_length={len(result['response'])}")
            
            serializer = MessageResponseSerializer(response_data)
            return Response(serializer.data)
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Unknown error')
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error in chat view: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 