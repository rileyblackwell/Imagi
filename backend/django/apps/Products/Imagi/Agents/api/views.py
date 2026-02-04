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

from ..services import ImagiAgentService, DEFAULT_MODEL

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
    
    This endpoint accepts a prompt and generates a response using GPT-5.2.
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
        
        # Default to GPT-5.2 if no model specified
        if not model:
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
