"""
API views for the Agents app.

These views handle the API endpoints for the Agents app, delegating business logic
to the ImagiAgentService which uses the OpenAI Agents SDK.
"""

import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import json
from django.views.decorators.csrf import csrf_exempt
import traceback

from django.utils import timezone
from django.shortcuts import get_object_or_404

from ..models import AgentConversation, AgentMessage
from ..services import ImagiAgentService, DEFAULT_MODEL

# Re-export for URL imports
__all__ = [
    'chat', 'agent', 'cors_preflight',
    'conversations_list_create', 'conversation_detail',
    'conversation_messages',
]

# Configure logging
logger = logging.getLogger(__name__)


def create_error_response(error, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR):
    """
    Create a properly rendered error response with CORS headers.
    """
    from rest_framework.renderers import JSONRenderer
    
    error_message = str(error)
    response = Response(
        {'error': error_message}, 
        status=status_code
    )
    
    response = add_cors_headers(response)
    
    if not hasattr(response, 'accepted_renderer') or not response.accepted_renderer:
        response.accepted_renderer = JSONRenderer()
    
    response.accepted_media_type = getattr(response, 'accepted_media_type', 'application/json')
    response.renderer_context = getattr(response, 'renderer_context', {})
    
    try:
        response.render()
    except Exception as e:
        logger.error(f"Error rendering response: {str(e)}")
        from django.http import HttpResponse
        return HttpResponse(
            content=json.dumps({'error': error_message}),
            content_type='application/json',
            status=status_code
        )
    
    return response


def add_cors_headers(response):
    """Add CORS headers to any response object."""
    response["Access-Control-Allow-Origin"] = "http://localhost:5174"
    response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Accept, X-Requested-With, x-csrftoken, x-api-client"
    response["Access-Control-Allow-Credentials"] = "true"
    response["Access-Control-Max-Age"] = "86400"
    return response


@api_view(['OPTIONS'])
@csrf_exempt
def cors_preflight(request):
    """Handle OPTIONS requests for CORS preflight checks."""
    response = Response()
    return add_cors_headers(response)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat(request):
    """
    Chat with an AI agent using the OpenAI Agents SDK.
    
    This endpoint accepts a prompt and generates a response using GPT 5.5.
    The conversation is threaded if a conversation_id is provided.
    """
    try:
        # Extract request data
        message = request.data.get('message')
        model = request.data.get('model', DEFAULT_MODEL)
        conversation_id = request.data.get('conversation_id')
        project_id = request.data.get('project_id')
        current_file = request.data.get('current_file')
        
        logger.info(f"Chat API request - Model: {model}, Project ID: {project_id}")
        
        # Validate required fields
        if not message:
            return create_error_response('Message is required', status.HTTP_400_BAD_REQUEST)
        
        # Force GPT 5.5 for chat mode
        if not model or model != DEFAULT_MODEL:
            model = DEFAULT_MODEL
        
        # Ensure project_id is an integer if provided
        if project_id:
            try:
                project_id = int(project_id)
            except (ValueError, TypeError):
                project_id = None
        
        # Ensure conversation_id is an integer if provided
        if conversation_id:
            try:
                conversation_id = int(conversation_id)
            except (ValueError, TypeError):
                conversation_id = None
        
        # Create agent service instance
        agent_service = ImagiAgentService(model=model)
        
        logger.info(f"Chat request: message length={len(message)}, model={model}, project_id={project_id}")
        
        # Process the chat message
        result = agent_service.process_chat(
            user_input=message,
            user=request.user,
            model=model,
            project_id=project_id,
            current_file=current_file,
            conversation_id=conversation_id,
        )
        
        # Check for success
        if not result.get('success', False):
            error_message = result.get('error', 'Error processing message')
            return create_error_response(error_message, status.HTTP_400_BAD_REQUEST)
        
        # Format the response
        response_data = {
            'conversation_id': result.get('conversation_id'),
            'response': result.get('response', ''),
            'single_message': result.get('single_message', True),
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in chat API: {str(e)}")
        logger.error(traceback.format_exc())
        return create_error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def agent(request):
    """
    Process a message using the Coding Agent (agent mode).

    The coding agent can both chat and edit project files using function tools
    from the OpenAI Agents SDK. It autonomously decides when to read/write files
    versus just responding conversationally.
    """
    try:
        message = request.data.get('message')
        model = request.data.get('model', DEFAULT_MODEL)
        conversation_id = request.data.get('conversation_id')
        project_id = request.data.get('project_id')
        current_file = request.data.get('current_file')

        logger.info(f"Agent API request - Model: {model}, Project ID: {project_id}")

        if not message:
            return create_error_response('Message is required', status.HTTP_400_BAD_REQUEST)

        if not project_id:
            return create_error_response('Project ID is required for agent mode', status.HTTP_400_BAD_REQUEST)

        # Force GPT 5.5 for agent mode
        if not model or model != DEFAULT_MODEL:
            model = DEFAULT_MODEL

        # Ensure project_id is an integer
        try:
            project_id = int(project_id)
        except (ValueError, TypeError):
            return create_error_response('Invalid project ID', status.HTTP_400_BAD_REQUEST)

        # Ensure conversation_id is an integer if provided
        if conversation_id:
            try:
                conversation_id = int(conversation_id)
            except (ValueError, TypeError):
                conversation_id = None

        # Create agent service instance
        agent_service = ImagiAgentService(model=model)

        logger.info(f"Agent request: message length={len(message)}, model={model}, project_id={project_id}")

        # Process the message with the coding agent
        result = agent_service.process_agent(
            user_input=message,
            user=request.user,
            model=model,
            project_id=project_id,
            current_file=current_file,
            conversation_id=conversation_id,
        )

        if not result.get('success', False):
            error_message = result.get('error', 'Error processing message')
            return create_error_response(error_message, status.HTTP_400_BAD_REQUEST)

        response_data = {
            'conversation_id': result.get('conversation_id'),
            'response': result.get('response', ''),
            'files_changed': result.get('files_changed', []),
            'single_message': result.get('single_message', True),
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error in agent API: {str(e)}")
        logger.error(traceback.format_exc())
        return create_error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)


# ---------------------------------------------------------------------------
# Conversation (agent instance) CRUD
# ---------------------------------------------------------------------------

def _serialize_conversation(conversation):
    last_message = conversation.messages.order_by('-created_at').first()
    preview = ''
    if last_message and last_message.content:
        preview = last_message.content.strip().splitlines()[0][:140]
    return {
        'id': conversation.id,
        'title': conversation.title or '',
        'mode': conversation.mode,
        'model_name': conversation.model_name,
        'project_id': conversation.project_id,
        'archived_at': conversation.archived_at.isoformat() if conversation.archived_at else None,
        'created_at': conversation.created_at.isoformat(),
        'updated_at': conversation.updated_at.isoformat(),
        'last_message_preview': preview,
    }


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def conversations_list_create(request):
    """List conversations for a project, or create a new one."""
    if request.method == 'GET':
        project_id = request.query_params.get('project_id')
        qs = AgentConversation.objects.filter(user=request.user)
        if project_id:
            try:
                qs = qs.filter(project_id=int(project_id))
            except (ValueError, TypeError):
                return create_error_response('Invalid project_id', status.HTTP_400_BAD_REQUEST)
        data = [_serialize_conversation(c) for c in qs.order_by('-updated_at')]
        return Response(data, status=status.HTTP_200_OK)

    # POST -> create
    try:
        project_id = request.data.get('project_id')
        mode = request.data.get('mode') or 'chat'
        model_name = request.data.get('model_name') or DEFAULT_MODEL
        title = (request.data.get('title') or '').strip()[:120]

        if project_id is not None:
            try:
                project_id = int(project_id)
            except (ValueError, TypeError):
                return create_error_response('Invalid project_id', status.HTTP_400_BAD_REQUEST)

        if mode not in ('chat', 'agent'):
            mode = 'chat'

        agent_service = ImagiAgentService(model=model_name)
        conversation = agent_service.create_conversation(
            user=request.user,
            model=model_name,
            project_id=project_id,
            mode=mode,
            title=title,
        )
        return Response(_serialize_conversation(conversation), status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}")
        logger.error(traceback.format_exc())
        return create_error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def conversation_detail(request, conversation_id):
    """Retrieve, update, or delete a single conversation."""
    conversation = get_object_or_404(
        AgentConversation, id=conversation_id, user=request.user
    )

    if request.method == 'GET':
        return Response(_serialize_conversation(conversation), status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        conversation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # PATCH
    updated_fields = []
    if 'title' in request.data:
        conversation.title = (request.data.get('title') or '').strip()[:120]
        updated_fields.append('title')
    if 'mode' in request.data:
        new_mode = request.data.get('mode')
        if new_mode in ('chat', 'agent'):
            conversation.mode = new_mode
            updated_fields.append('mode')
    if 'model_name' in request.data:
        conversation.model_name = request.data.get('model_name') or conversation.model_name
        updated_fields.append('model_name')
    if 'archived' in request.data:
        archived = bool(request.data.get('archived'))
        conversation.archived_at = timezone.now() if archived else None
        updated_fields.append('archived_at')

    if updated_fields:
        conversation.save(update_fields=updated_fields + ['updated_at'])

    return Response(_serialize_conversation(conversation), status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversation_messages(request, conversation_id):
    """Return messages for a conversation."""
    conversation = get_object_or_404(
        AgentConversation, id=conversation_id, user=request.user
    )
    messages = [
        {
            'id': m.id,
            'role': m.role,
            'content': m.content,
            'timestamp': m.created_at.isoformat(),
        }
        for m in conversation.messages.order_by('created_at')
    ]
    return Response(messages, status=status.HTTP_200_OK)
