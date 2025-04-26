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
from ..services import ChatAgentService, TemplateAgentService, StylesheetAgentService


logger = logging.getLogger(__name__)

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
            
        # Validate project access
        project, error = template_agent.validate_project_access(project_id, request.user)
        if error:
            return create_error_response(error['error'], status.HTTP_400_BAD_REQUEST)
            
        # Set project files if available
        if project_files:
            template_agent.project_files = project_files
            
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
        data = request.data
        message = data.get('message')
        model = data.get('model', 'claude-3-7-sonnet-20250219')
        project_id = data.get('project_id')
        file_path = data.get('file_path')
        conversation_id = data.get('conversation_id')
        project_files = data.get('project_files', [])

        # Validate required fields
        if not message:
            return create_error_response('Message is required', status.HTTP_400_BAD_REQUEST)

        if not project_id:
            return create_error_response('Project ID is required', status.HTTP_400_BAD_REQUEST)

        if not file_path:
            return create_error_response('File path is required', status.HTTP_400_BAD_REQUEST)

        # Initialize stylesheet agent
        stylesheet_agent = StylesheetAgentService()
        
        # Validate project access
        project, error = stylesheet_agent.validate_project_access(project_id, request.user)
        if error:
            return create_error_response(error['error'], status.HTTP_400_BAD_REQUEST)
                
        # Add project files to the agent context if provided
        if project_files:
            stylesheet_agent.project_files = project_files
            logger.info(f"Added {len(project_files)} project files to stylesheet context")

        # Process the stylesheet
        result = stylesheet_agent.process_stylesheet(
            prompt=message,
            model=model,
            user=request.user,
            project_id=project_id,
            file_path=file_path,
            conversation_id=conversation_id
        )
        
        # Return the result
        if result.get('success'):
            response = Response(result)
            return add_cors_headers(response)
        else:
            return create_error_response(result.get('error', 'Unknown error'), status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error in build_stylesheet view: {str(e)}")
        logger.error(traceback.format_exc())
        return create_error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST', 'OPTIONS'])
@csrf_exempt
def chat(request):
    """
    API endpoint for chatting with AI agents.
    
    POST: Send a message to the AI agent and get a response.
    Required parameters: message (str), model (str), project_id (str)
    Optional parameters: conversation_id (str), mode (str), current_file (dict)
    
    GET: Retrieve conversation history.
    Required parameter: conversation_id (str)
    
    OPTIONS: Handle CORS preflight requests
    """
    # Handle OPTIONS requests for CORS
    if request.method == 'OPTIONS':
        response = cors_preflight(request)
        response['Cache-Control'] = 'no-cache'
        return response
        
    # Check authentication
    if not request.user.is_authenticated:
        return create_error_response('Authentication required', status.HTTP_401_UNAUTHORIZED)
    
    # Create service instance
    try:
        chat_service = ChatAgentService()
    except Exception as service_error:
        logger.error(f"Failed to initialize ChatAgentService: {str(service_error)}")
        return create_error_response(f"Service initialization failed: {str(service_error)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Helper function to check model credits
    def check_model_credits(user, model_id):
        """
        Check if the user has sufficient credits for the selected model.
        
        Args:
            user: The Django user object
            model_id: The model ID to use
            
        Returns:
            tuple: (has_credits, error_dict)
        """
        try:
            # Log the model ID being checked
            logger.info(f"Checking credits for model: {model_id}")
            
            # Import get_model_cost from model_definitions for centralized pricing
            from ..services.model_definitions import get_model_cost
            
            # Import CreditBalance model directly
            from apps.Payments.models import CreditBalance
            
            # Get consistent model price from the centralized get_model_cost function
            required_amount = get_model_cost(model_id)
            logger.info(f"Model cost for {model_id}: ${required_amount}")
            
            # Get user's credit balance directly from the CreditBalance model
            try:
                credit_balance = CreditBalance.objects.get(user=user)
                balance = float(credit_balance.balance)
            except CreditBalance.DoesNotExist:
                # Create a new balance record with zero balance if it doesn't exist
                credit_balance = CreditBalance.objects.create(user=user, balance=0)
                balance = 0.0
            
            # Log for debugging
            logger.info(f"Credit check: user={user.username}, model={model_id}, balance=${balance:.4f}, required=${required_amount:.4f}")
            
            # Use a small epsilon value to handle floating-point precision issues
            epsilon = 0.0001
            if balance + epsilon < required_amount:
                logger.warning(f"Insufficient credits for {model_id}: ${balance:.4f} available, ${required_amount:.4f} required")
                return False, {
                    'error': f"Insufficient credits: You need ${required_amount - balance:.4f} more to use {model_id}. Please add more credits."
                }
                
            logger.info(f"Credit check passed for {model_id}: ${balance:.4f} available, ${required_amount:.4f} required")
            return True, None
            
        except AttributeError as attr_error:
            logger.error(f"AttributeError checking credits: {str(attr_error)}")
            return False, {'error': f"Credit balance error: {str(attr_error)}. Please contact support."}
        except Exception as e:
            logger.error(f"Error checking credits: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False, {'error': f"Error checking credits: {str(e)}"}
    
    # GET request - retrieve conversation history
    if request.method == 'GET':
        # Check for conversation_id
        conversation_id = request.query_params.get('conversation_id')
        if not conversation_id:
            return create_error_response('conversation_id is required', status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get conversation history
            conversation_data = chat_service.get_conversation_history(conversation_id, request.user)
            response = Response(conversation_data)
            return add_cors_headers(response)
        except Exception as e:
            logger.error(f"Error retrieving conversation: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return create_error_response(str(e), status.HTTP_404_NOT_FOUND)
    
    # POST request - send message to AI
    elif request.method == 'POST':
        # Log request data for debugging
        logger.info(f"Chat API request received from user {request.user.username}")
        
        try:
            # Get required fields
            user_input = request.data.get('message')
            model_id = request.data.get('model')
            project_id = request.data.get('project_id')
            
            # Get optional fields
            conversation_id = request.data.get('conversation_id')
            mode = request.data.get('mode', 'chat')  # Default to chat mode
            current_file = request.data.get('current_file')
            
            # Log request parameters (excluding sensitive content)
            logger.info(f"Chat API parameters: model={model_id}, project_id={project_id}, " 
                        f"conversation_id={conversation_id}, mode={mode}, "
                        f"has_current_file={bool(current_file)}")
            
            # Check for required fields
            missing_fields = []
            if not user_input:
                missing_fields.append('message')
            if not model_id:
                missing_fields.append('model')
            if not project_id:
                missing_fields.append('project_id')
                
            if missing_fields:
                error_msg = f"Missing required parameters: {', '.join(missing_fields)}"
                logger.warning(f"Chat API request missing fields: {error_msg}")
                return create_error_response(error_msg, status.HTTP_400_BAD_REQUEST)
            
            # Validate model_id format - ensure it matches an expected pattern
            from ..services.model_definitions import MODELS
            
            if model_id not in MODELS:
                error_msg = f"Invalid model ID: {model_id}. Expected one of: {', '.join(MODELS.keys())}"
                logger.warning(f"Invalid model ID: {model_id}")
                return create_error_response(error_msg, status.HTTP_400_BAD_REQUEST)
            
            # Check user credits - using the view-specific helper to prevent overcharging
            try:
                has_credits, error = check_model_credits(request.user, model_id)
                if not has_credits:
                    logger.warning(f"Insufficient credits for user {request.user.username} to use {model_id}")
                    return create_error_response(error['error'], status.HTTP_400_BAD_REQUEST)
            except Exception as credit_error:
                logger.error(f"Error checking credits: {str(credit_error)}")
                return create_error_response(f"Credit check error: {str(credit_error)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Validate current file if provided
            if current_file:
                try:
                    is_valid, error = chat_service.validate_current_file(current_file)
                    if not is_valid:
                        logger.warning(f"Invalid current_file format: {error.get('error')}")
                        return create_error_response(error['error'], status.HTTP_400_BAD_REQUEST)
                except Exception as file_error:
                    logger.error(f"Error validating current file: {str(file_error)}")
                    return create_error_response(f"File validation error: {str(file_error)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Process message using service
            logger.info(f"Processing chat message for user {request.user.username} with model {model_id}")
            try:
                response_data = chat_service.process_message(
                    user_input, 
                    model_id, 
                    request.user,
                    conversation_id,
                    project_id,
                    current_file,
                    mode == 'build'
                )
            except Exception as process_error:
                logger.error(f"Error in process_message: {str(process_error)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                return create_error_response(f"Error processing message: {str(process_error)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Check for success or error
            if not response_data.get('success', False):
                logger.warning(f"Chat process failed: {response_data.get('error', 'Unknown error')}")
                return create_error_response(
                    response_data.get('error', 'Failed to process message'), 
                    status.HTTP_400_BAD_REQUEST
                )
            
            # Add CORS headers to successful response
            logger.info(f"Chat message processed successfully for user {request.user.username}")
            response = Response(response_data)
            return add_cors_headers(response)
            
        except ValueError as ve:
            # Handle validation errors
            logger.error(f"Validation error in chat view: {str(ve)}")
            return create_error_response(str(ve), status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Error processing chat message: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return create_error_response(f"Server error processing chat message: {str(e)}")
        
    # This should never happen, but just in case
    return create_error_response('Method not allowed', status.HTTP_405_METHOD_NOT_ALLOWED)

