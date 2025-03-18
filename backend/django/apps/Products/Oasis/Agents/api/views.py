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
# Import services from the barrel file
from ..services import ChatAgentService, TemplateAgentService, StylesheetAgentService

logger = logging.getLogger(__name__)

# Initialize agent services
template_agent = TemplateAgentService()
stylesheet_agent = StylesheetAgentService()
chat_agent = ChatAgentService()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def build_template(request):
    """
    Handle template generation and updates in build mode.
    
    This endpoint processes user prompts in build mode, sends them to the selected AI model
    with the current file context, then updates the specified file with the generated code.
    """
    try:
        # Extract request data
        user_input = request.data.get('message')
        model = request.data.get('model', 'claude-3-5-sonnet-20241022')
        file_path = request.data.get('file_path')
        conversation_id = request.data.get('conversation_id')
        
        # Validate required fields
        if not all([user_input, file_path]):
            return Response({
                'error': 'Missing required fields - message and file_path are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Delegate to template agent service
        result = template_agent.handle_template_request(
            user_input=user_input,
            model=model,
            user=request.user,
            file_path=file_path,
            conversation_id=conversation_id
        )
        
        # Process result
        if result.get('success'):
            # Prepare the response data with user and assistant messages
            response_data = {
                'success': True,
                'conversation_id': result['conversation_id'],
                'response': result['response'],
                'file_path': file_path,
                'file_updated': result.get('file_updated', False),
                'user_message': {
                    'role': 'user',
                    'content': user_input,
                    'timestamp': result.get('timestamp')
                },
                'assistant_message': {
                    'role': 'assistant',
                    'content': result['response'],
                    'code': result.get('code', ''),
                    'timestamp': result.get('timestamp')
                }
            }
            
            serializer = MessageResponseSerializer(response_data)
            return Response(serializer.data)
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
    """Handle stylesheet generation requests."""
    try:
        # Extract request data
        user_input = request.data.get('message')
        model = request.data.get('model', 'claude-3-5-sonnet-20241022')
        file_path = request.data.get('file_path')
        conversation_id = request.data.get('conversation_id')
        
        # Validate required fields
        if not all([user_input, file_path]):
            return Response({
                'error': 'Missing required fields'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Delegate to service
        result = stylesheet_agent.handle_stylesheet_request(
            user_input=user_input,
            model=model,
            user=request.user,
            file_path=file_path,
            conversation_id=conversation_id
        )
        
        # Process result
        if result.get('success'):
            # Use the MessageResponseSerializer for consistent formatting
            response_data = {
                'success': True,
                'conversation_id': result['conversation_id'],
                'response': result['response'],
                'user_message': result['user_message'],
                'assistant_message': result['assistant_message']
            }
            serializer = MessageResponseSerializer(response_data)
            return Response(serializer.data)
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Unknown error')
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error in build_stylesheet: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat(request):
    """
    Handle chat mode AI interactions.
    
    This endpoint processes user prompts in chat mode, sends them to the selected AI model,
    and returns the AI's response for display in the chat interface.
    """
    try:
        # Extract request data
        user_input = request.data.get('message')
        model = request.data.get('model', 'claude-3-5-sonnet-20241022')
        conversation_id = request.data.get('conversation_id')
        project_path = request.data.get('project_path')
        
        # Validate required fields
        if not user_input:
            return Response({
                'error': 'Message is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Delegate to the chat agent service
        result = chat_agent.process_conversation(
            user_input=user_input,
            model=model,
            user=request.user,
            conversation_id=conversation_id,
            project_path=project_path
        )
        
        # Process result
        if result.get('success'):
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