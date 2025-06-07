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
import json
from django.views.decorators.csrf import csrf_exempt
import traceback


# Import services when needed, not at module level
from ..services import ChatAgentService, TemplateAgentService

# Add more detailed logging for StylesheetAgentService import
logger = logging.getLogger(__name__)
logger.info("Attempting to import StylesheetAgentService...")

# Try to import StylesheetAgentService, which might not be available
try:
    # First check if the file exists
    import os
    
    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    stylesheet_path = os.path.join(current_dir, 'services', 'stylesheet_agent_service.py')
    
    logger.info(f"Looking for stylesheet_agent_service.py at: {stylesheet_path}")
    if os.path.exists(stylesheet_path):
        logger.info(f"File exists! Attempting import...")
        
    # Try the actual import
    from ..services import StylesheetAgentService
    has_stylesheet_service = True
    logger.info("Successfully imported StylesheetAgentService")
except ImportError as e:
    logger.error(f"Failed to import StylesheetAgentService: {str(e)}")
    logger.error(traceback.format_exc())
    has_stylesheet_service = False
    # Create a fallback error function
    def stylesheet_service_not_available(error_message="Stylesheet service not available"):
        def service_error(*args, **kwargs):
            return {
                'success': False,
                'error': error_message
            }
        return service_error
except Exception as e:
    logger.error(f"Unexpected error importing StylesheetAgentService: {str(e)}")
    logger.error(traceback.format_exc())
    has_stylesheet_service = False
    
logger.info(f"Stylesheet service availability: {has_stylesheet_service}")

# Helper function to create error responses that are properly rendered
def create_error_response(error, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR):
    """
    Create a properly rendered error response with CORS headers.
    This solves the ContentNotRenderedError issue when middleware tries to access response.content.
    
    Args:
        error: Exception object or error string
        status_code: HTTP status code to return
        
    Returns:
        Pre-rendered Response object with CORS headers
    """
    from rest_framework.response import Response
    from rest_framework.renderers import JSONRenderer
    
    # Create response object
    error_message = str(error)
    response = Response(
        {'error': error_message}, 
        status=status_code
    )
    
    # Add CORS headers
    response = add_cors_headers(response)
    
    # Ensure the renderer is set
    if not hasattr(response, 'accepted_renderer') or not response.accepted_renderer:
        response.accepted_renderer = JSONRenderer()
    
    response.accepted_media_type = getattr(response, 'accepted_media_type', 'application/json')
    response.renderer_context = getattr(response, 'renderer_context', {})
    
    # Explicitly render the response
    try:
        response.render()
    except Exception as e:
        # If rendering fails, create a basic response that will definitely work
        logger.error(f"Error rendering response: {str(e)}")
        from django.http import HttpResponse
        return HttpResponse(
            content=json.dumps({'error': error_message}),
            content_type='application/json',
            status=status_code
        )
    
    return response

# Additional function to ensure CORS headers are set on any response object
def add_cors_headers(response):
    """
    Add CORS headers to any response object.
    This is a helper function to ensure all responses have CORS headers.
    """
    # Allow specific origins or all origins in development
    response["Access-Control-Allow-Origin"] = "http://localhost:5174"
    response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Accept, X-Requested-With, x-csrftoken, x-api-client"
    response["Access-Control-Allow-Credentials"] = "true"
    response["Access-Control-Max-Age"] = "86400"  # 24 hours
    return response

# Add CORS preflight handler function
@api_view(['OPTIONS'])
@csrf_exempt
def cors_preflight(request):
    """
    Handle OPTIONS requests for CORS preflight checks.
    This function returns an empty response with appropriate CORS headers.
    """
    response = Response()
    return add_cors_headers(response)

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
        model = request.data.get('model', 'claude-3-7-sonnet-20250219')
        project_id = request.data.get('project_id')
        file_path = request.data.get('file_path', 'index.html')
        conversation_id = request.data.get('conversation_id')
        project_files = request.data.get('project_files', [])
        
        # Initialize the agent service
        template_agent = TemplateAgentService()
        
        # Validate required fields
        if not message:
            return create_error_response('Message is required', status.HTTP_400_BAD_REQUEST)
            
        if not project_id:
            return create_error_response('Project ID is required', status.HTTP_400_BAD_REQUEST)
        
        # Ensure project_id is a string
        project_id = str(project_id)
            
        # Validate project access
        project, error = template_agent.validate_project_access(project_id, request.user)
        if error:
            return create_error_response(error['error'], status.HTTP_400_BAD_REQUEST)
        
        # Load project files if not provided in the request
        if not project_files and project and project.project_path:
            try:
                project_files = template_agent.load_project_files(project.project_path)
                logger.info(f"Loaded {len(project_files)} project files from server for context")
            except Exception as e:
                logger.warning(f"Could not load project files: {str(e)}")
        
        # Set project files on the agent
        if project_files:
            template_agent.project_files = project_files
            logger.info(f"Added {len(project_files)} project files to template context")
            
        # Process the template request
        result = template_agent.process_template(
            prompt=message,
            model=model,
            user=request.user,
            project_id=project_id,
            file_name=file_path,
            conversation_id=conversation_id
        )
        
        # Return success or error response
        if result.get('success'):
            response = Response(result)
            return add_cors_headers(response)
        else:
            return create_error_response(result.get('error', 'Unknown error'), status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error in build_template view: {str(e)}")
        logger.error(traceback.format_exc())
        return create_error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def build_stylesheet(request):
    """
    API view for building CSS stylesheets using AI.

    This endpoint accepts a POST request with user prompt, model, project ID,
    and target file path to generate a CSS stylesheet using the AI models.

    Returns:
        Response: A Django REST Framework response containing the generated CSS
    """
    try:
        # Check if StylesheetAgentService is available
        if not has_stylesheet_service:
            logger.error("StylesheetAgentService is not available - import failed")
            return create_error_response(
                'Stylesheet generation service is not available in this installation',
                status.HTTP_501_NOT_IMPLEMENTED
            )
            
        data = request.data
        message = data.get('message')
        model = data.get('model', 'claude-3-7-sonnet-20250219')
        project_id = data.get('project_id')
        file_path = data.get('file_path')
        conversation_id = data.get('conversation_id')
        project_files = data.get('project_files', [])

        # Log the request details
        logger.info(f"Stylesheet build request: file={file_path}, model={model}, project_id={project_id}")

        # Validate required fields
        if not message:
            return create_error_response('Message is required', status.HTTP_400_BAD_REQUEST)

        if not project_id:
            return create_error_response('Project ID is required', status.HTTP_400_BAD_REQUEST)
            
        # Ensure project_id is a string
        project_id = str(project_id)

        if not file_path:
            return create_error_response('File path is required', status.HTTP_400_BAD_REQUEST)

        # Initialize stylesheet agent
        try:
            stylesheet_agent = StylesheetAgentService()
            logger.info("StylesheetAgentService initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing StylesheetAgentService: {str(e)}")
            logger.error(traceback.format_exc())
            return create_error_response(f"Error initializing stylesheet service: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Validate project access
        try:
            project, error = stylesheet_agent.validate_project_access(project_id, request.user)
            if error:
                logger.error(f"Project access validation failed: {error['error']}")
                return create_error_response(error['error'], status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error validating project access: {str(e)}")
            return create_error_response(f"Error validating project: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Load project files if not provided in the request
        if not project_files and project and project.project_path:
            try:
                project_files = stylesheet_agent.load_project_files(project.project_path)
                logger.info(f"Loaded {len(project_files)} project files from server for context")
            except Exception as e:
                logger.warning(f"Could not load project files: {str(e)}")
                
        # Add project files to the agent context if provided
        if project_files:
            stylesheet_agent.project_files = project_files
            logger.info(f"Added {len(project_files)} project files to stylesheet context")

        # Process the stylesheet
        try:
            logger.info(f"Processing stylesheet with prompt length: {len(message)}")
            result = stylesheet_agent.process_stylesheet(
                prompt=message,
                model=model,
                user=request.user,
                project_id=project_id,
                file_path=file_path,
                conversation_id=conversation_id
            )
            logger.info(f"Stylesheet processing result: success={result.get('success', False)}")
            
            # Log response structure for debugging
            logger.debug(f"Stylesheet result keys: {list(result.keys() if result else [])}")
            
            # Check for empty response
            if result.get('success') and not result.get('response', '').strip():
                logger.warning("Stylesheet result is empty despite success=True")
                result['response'] = "/* Default stylesheet - no specific styles generated */"
                result['code'] = result['response']
            
        except Exception as e:
            logger.error(f"Error processing stylesheet: {str(e)}")
            logger.error(traceback.format_exc())
            return create_error_response(f"Error generating stylesheet: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Return the result
        if result.get('success'):
            response = Response(result)
            return add_cors_headers(response)
        else:
            logger.warning(f"Stylesheet generation failed: {result.get('error', 'Unknown error')}")
            return create_error_response(result.get('error', 'Unknown error'), status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error in build_stylesheet view: {str(e)}")
        logger.error(traceback.format_exc())
        return create_error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat(request):
    """
    Chat with an AI agent.
    
    This endpoint accepts a prompt and generates a response using the selected AI model.
    The conversation is threaded if a conversation_id is provided.
    """
    try:
        # Extract request data
        message = request.data.get('message')
        model = request.data.get('model', 'claude-3-7-sonnet-20250219')
        conversation_id = request.data.get('conversation_id')
        mode = request.data.get('mode', 'chat')
        project_id = request.data.get('project_id')
        current_file = request.data.get('current_file')
        project_files = request.data.get('project_files', [])
        
        # Explicitly check for build mode flag
        is_build_mode = request.data.get('is_build_mode', False)
        if not is_build_mode and mode == 'build':
            is_build_mode = True
        
        logger.info(f"Chat API request - Mode: {mode}, Build Mode: {is_build_mode}, Model: {model}")
        
        # Validate required fields
        if not message:
            return create_error_response('Message is required', status.HTTP_400_BAD_REQUEST)
        
        # Validate model
        if not model:
            model = 'claude-3-7-sonnet-20250219'  # Default model
            
        # Ensure project_id is a string if provided
        if project_id:
            project_id = str(project_id)
            
        # Create agent instance
        chat_agent = ChatAgentService()
        
        # Optionally add project files to the agent context
        if project_files:
            chat_agent.project_files = project_files
            logger.info(f"Added {len(project_files)} project files to chat context")
        
        # Log the complete request payload
        logger.info(f"Chat request payload: message length={len(message)}, model={model}, project_id={project_id}, is_build_mode={is_build_mode}")
        
        # Process the message
        result = chat_agent.process_message(
            user_input=message,
            model_id=model,
            user=request.user,
            conversation_id=conversation_id,
            project_id=project_id,
            current_file=current_file,
            is_build_mode=is_build_mode
        )
        
        # Check for success
        if not result.get('success', False):
            error_code = status.HTTP_400_BAD_REQUEST
            error_message = result.get('error', 'Error processing message')
            
            # Check for specific error types
            if 'Insufficient credits' in error_message:
                error_code = status.HTTP_402_PAYMENT_REQUIRED
            
            return create_error_response(error_message, error_code)
        
        # Format the response
        response_data = {
            'conversation_id': result.get('conversation_id'),
            'response': result.get('response', ''),
            'timestamp': result.get('timestamp', None)
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in chat API: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return create_error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)

