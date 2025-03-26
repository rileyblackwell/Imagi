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
from django.http import StreamingHttpResponse
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
        
        if not message:
            return Response({
                'error': 'Message is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Initialize the agent service
        template_agent = TemplateAgentService()
            
        # Log request
        logger.info(f"Template request: message={message}, model={model}, file_path={file_path}, project_id={project_id}")
        
        # Process the template request
        result = template_agent.process_template(
            prompt=message,
            model=model,
            user=request.user,
            project_id=project_id,
            file_name=file_path,
            conversation_id=conversation_id
        )
        
        # Use service method to format the response
        response_data = template_agent.build_template_response(result, message, file_path)
        
        if response_data.get('success'):
            return Response(response_data)
        else:
            return Response({
                'success': False,
                'error': response_data.get('error', 'Unknown error')
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
        model = request.data.get('model', 'claude-3-7-sonnet-20250219')
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
        
        # Return the result directly as it's already formatted appropriately in the service
        return Response(result)
            
    except Exception as e:
        logger.error(f"[ERROR] Unhandled exception in build_stylesheet view: {str(e)}")
        logger.error(f"[ERROR] Traceback: {traceback.format_exc()}")
        
        # Use the service's default stylesheet fallback
        try:
            # Initialize the agent service
            stylesheet_agent = StylesheetAgentService()
            
            # Generate fallback stylesheet
            fallback_result = stylesheet_agent.process_stylesheet(
                prompt="Generate a minimal default stylesheet with basic styling",
                model="claude-3-7-sonnet-20250219",
                user=request.user,
                file_path=file_path or 'static/css/styles.css'
            )
            
            # Log the fallback
            logger.info(f"[INFO] Returning fallback stylesheet due to error")
            
            # Return the fallback result
            return Response(fallback_result)
        except Exception as recovery_error:
            logger.error(f"[ERROR] Error recovery also failed: {str(recovery_error)}")
            # As a last resort, return the error
            return Response({
                'success': False,
                'error': f"Server error: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST', 'OPTIONS'])
@csrf_exempt
def chat(request):
    """
    API endpoint for chatting with AI agents.
    
    POST: Send a message to the AI agent and get a response.
    Required parameters: message (str), model (str), project_id (str)
    Optional parameters: conversation_id (str), mode (str), current_file (dict), stream (bool)
    
    GET: Retrieve conversation history.
    Required parameter: conversation_id (str)
    
    OPTIONS: Handle CORS preflight requests
    """
    # Handle OPTIONS requests for CORS
    if request.method == 'OPTIONS':
        response = cors_preflight(request)
        # Ensure streaming-related headers are set for OPTIONS requests
        response['Cache-Control'] = 'no-cache'
        response['Connection'] = 'keep-alive'
        response['X-Accel-Buffering'] = 'no'
        return response
        
    # Check authentication
    if not request.user.is_authenticated:
        return create_error_response('Authentication required', status.HTTP_401_UNAUTHORIZED)
    
    # Log the API call with more details for debugging
    logger.info(f"Chat API called by {request.user.username} with method {request.method}")
    logger.info(f"Request headers: {dict(request.headers)}")
    logger.info(f"CORS details: Origin: {request.headers.get('Origin')}, Method: {request.method}")
    
    # Debug: Log user balance
    try:
        from apps.Payments.services.credit_service import CreditService
        from ..services.agent_service import MODEL_COSTS
        credit_service = CreditService()
        user_balance = credit_service.get_balance(request.user)
        logger.info(f"Current user balance for {request.user.username}: ${user_balance}")
    except Exception as balance_error:
        logger.error(f"Error retrieving user balance: {str(balance_error)}")
    
    # Debug: Log the full request data
    logger.debug(f"Request data: {request.data}")
    logger.debug(f"Request query params: {request.query_params}")
    logger.debug(f"Request headers: {request.headers}")
    
    # Create service instance
    chat_service = ChatAgentService()
    
    # Handle CSRF token for forms
    if request.method == 'POST' and request.headers.get('X-CSRFToken'):
        pass  # CSRF validation is bypassed with @csrf_exempt but token is provided
    
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
            response = Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
            return add_cors_headers(response)
    
    # POST request - send message to AI
    elif request.method == 'POST':
        # Get required fields
        user_input = request.data.get('message')
        model_id = request.data.get('model')
        project_id = request.data.get('project_id')
        
        # Get optional fields
        conversation_id = request.data.get('conversation_id')
        mode = request.data.get('mode', 'chat')  # Default to chat mode
        current_file = request.data.get('current_file')
        stream = request.data.get('stream', False)
        
        # Debug logging
        logger.debug(f"Chat request data: {request.data}")
        
        # Check for required fields
        missing_fields = []
        if not user_input:
            missing_fields.append('message')
            logger.error("Missing required parameter: message")
        if not model_id:
            missing_fields.append('model')
            logger.error("Missing required parameter: model")
        if not project_id:
            missing_fields.append('project_id')
            logger.error("Missing required parameter: project_id")
            
        if missing_fields:
            error_msg = f"Missing required parameters: {', '.join(missing_fields)}"
            return create_error_response(error_msg, status.HTTP_400_BAD_REQUEST)
        
        # Log model cost for this request
        from ..services.agent_service import MODEL_COSTS
        model_cost = MODEL_COSTS.get(model_id, 0.04)
        
        # Special handling for gpt-4o-mini to ensure correct cost
        if model_id == 'gpt-4o-mini':
            # Force the cost to be 0.005 regardless of what's in MODEL_COSTS
            model_cost = 0.005
            logger.info(f"Using fixed cost of $0.005 for gpt-4o-mini regardless of MODEL_COSTS value")
        
        logger.info(f"Model {model_id} cost from MODEL_COSTS: ${model_cost}")
        
        # Check user credits directly before continuing
        from apps.Payments.services.credit_service import CreditService
        credit_service = CreditService()
        user_balance = credit_service.get_balance(request.user)
        logger.info(f"User balance for {request.user.username}: ${user_balance} - Required for {model_id}: ${model_cost}")
        
        # Use an epsilon value to handle floating point precision
        epsilon = 0.0001
        if user_balance + epsilon < model_cost:
            needed_amount = max(0, model_cost - user_balance)
            
            # Special handling for gpt-4o-mini pricing error pattern
            if model_id == 'gpt-4o-mini' and abs(needed_amount - 0.035) < 0.001:
                # This is the classic $0.04 vs $0.005 error pattern
                logger.warning(f"Detected the common gpt-4o-mini pricing error pattern. User has ${user_balance}, needs ${model_cost}, system calculated ${needed_amount} needed")
                logger.warning(f"Allowing this gpt-4o-mini request to proceed despite the error pattern")
                # Continue with processing - do not return an error
            # Only report error if difference is significant (greater than 0.001)
            elif needed_amount > 0.001:
                logger.error(f"Insufficient credits for {request.user.username}. " 
                           f"Has: ${user_balance}, Needs: ${model_cost}, "
                           f"Missing: ${needed_amount}")
                error_msg = f"Insufficient credits: You need ${needed_amount:.2f} more to use {model_id}. Please add more credits."
                return create_error_response(error_msg, status.HTTP_400_BAD_REQUEST)
            else:
                # If difference is negligible, proceed
                logger.info(f"Negligible credit difference (${needed_amount:.5f}), allowing request to proceed")
        else:
            logger.info(f"User {request.user.username} has sufficient credits. Balance: ${user_balance}, Required: ${model_cost}")
        
        # Validate current_file format if provided
        if current_file and not isinstance(current_file, dict):
            logger.error(f"Invalid current_file format: {current_file}")
            return create_error_response('current_file must be a dictionary with path, content, and type', 
                        status.HTTP_400_BAD_REQUEST)
        
        # Check current_file has required fields if provided
        if current_file and isinstance(current_file, dict):
            required_fields = ['path', 'type']
            missing_required = [field for field in required_fields if field not in current_file]
            if missing_required:
                logger.error(f"Missing required fields in current_file: {missing_required}")
                return create_error_response(f"current_file must contain {', '.join(required_fields)} fields", 
                            status.HTTP_400_BAD_REQUEST)
            
            # If content is not provided, we'll fetch it later if needed
            if 'content' not in current_file:
                logger.info(f"current_file missing content field, will be fetched as needed")
        
        # Determine if we're in build mode
        is_build_mode = mode == 'build'
        
        # Log details of the request
        logger.info(f"Chat request: model={model_id}, user={request.user.username}, stream={stream}, mode={mode}")
        
        # In build mode, always use non-streaming API
        if is_build_mode:
            logger.info("Build mode detected, using non-streaming API")
            stream = False
        
        # Stream response if requested and supported
        if stream and not is_build_mode:
            try:
                conversation, api_messages, error_message = chat_service.process_message_stream(
                    user_input, 
                    model_id, 
                    request.user,
                    conversation_id,
                    project_id,
                    current_file
                )
                
                # Check for errors in preparation
                if error_message:
                    logger.error(f"Error preparing streaming response: {error_message}")
                    # Return a streaming response with error
                    response = StreamingHttpResponse(
                        (f"data: {json.dumps({'event': 'error', 'data': error_message})}\n\n" for _ in range(1)),
                        content_type='text/event-stream'
                    )
                    # Add CORS headers
                    response = add_cors_headers(response)
                    response['Cache-Control'] = 'no-cache'
                    response['Connection'] = 'keep-alive'
                    response['X-Accel-Buffering'] = 'no'
                    return response
                
                # Define stream_response function before using it
                def stream_response():
                    """
                    Generator function for streaming the AI response.
                    """
                    # Complete response for saving to database
                    full_response = ""
                    
                    try:
                        # Log the streaming attempt
                        logger.info(f"Starting streaming response with model {model_id} for user {request.user.username}")
                        
                        # Send event: conversation_id
                        data = json.dumps({"event": "conversation_id", "data": str(conversation.id)})
                        yield f"data: {data}\n\n"
                        
                        try:
                            if 'gpt' in model_id:
                                try:
                                    # Check if OpenAI client is available
                                    if not chat_service.openai_client:
                                        raise ValueError("OpenAI client not initialized properly")
                                    
                                    # Special logging for gpt-4o-mini
                                    if model_id == 'gpt-4o-mini':
                                        logger.info(f"Preparing to stream gpt-4o-mini response for user {request.user.username} with actual cost ${model_cost}")
                                    
                                    # Use the service method instead of direct client call
                                    stream = chat_service._generate_openai_stream(api_messages, model_id)
                                    
                                    # Stream the chunks
                                    for chunk in stream:
                                        content = chunk.choices[0].delta.content
                                        if content is not None:
                                            # Update full response
                                            full_response += content
                                            
                                            # Send content chunk
                                            data = json.dumps({"event": "content", "data": content})
                                            yield f"data: {data}\n\n"
                                except Exception as openai_error:
                                    logger.error(f"OpenAI streaming error: {str(openai_error)}")
                                    logger.exception(openai_error)  # Log full traceback
                                    error_msg = str(openai_error)
                                    if len(error_msg) > 200:  # Trim very long error messages
                                        error_msg = error_msg[:200] + "..."
                                    data = json.dumps({"event": "error", "data": error_msg})
                                    yield f"data: {data}\n\n"
                                    raise
                            
                            elif 'claude' in model_id:
                                # Use Anthropic's streaming API
                                try:
                                    # Check if Anthropic client is available
                                    if not chat_service.anthropic_client:
                                        raise ValueError("Anthropic client not initialized properly")
                                    
                                    logger.info(f"Starting claude streaming with model: {model_id}")
                                    # Get the stream object with proper error handling
                                    try:
                                        stream = chat_service._generate_anthropic_stream(api_messages, model_id)
                                    except Exception as client_error:
                                        logger.error(f"Failed to create Anthropic stream: {str(client_error)}")
                                        error_msg = f"Failed to initialize Claude stream: {str(client_error)}"
                                        data = json.dumps({"event": "error", "data": error_msg})
                                        yield f"data: {data}\n\n"
                                        return
                                    
                                    # Process the stream
                                    logger.info("Processing Claude stream")
                                    text_content = ""
                                    try:
                                        with stream as response:
                                            for text in response.text_stream:
                                                # Update full response
                                                full_response += text
                                                text_content += text
                                                
                                                # Send content chunk
                                                data = json.dumps({"event": "content", "data": text})
                                                yield f"data: {data}\n\n"
                                    except Exception as stream_error:
                                        logger.error(f"Error in Claude stream processing: {str(stream_error)}")
                                        if not text_content:  # No text was streamed
                                            error_msg = f"Claude streaming error: {str(stream_error)}"
                                            data = json.dumps({"event": "error", "data": error_msg})
                                            yield f"data: {data}\n\n"
                                        raise
                                except Exception as claude_error:
                                    logger.error(f"Claude streaming error: {str(claude_error)}")
                                    logger.exception(claude_error)  # Log full traceback
                                    error_msg = str(claude_error)
                                    if len(error_msg) > 200:  # Trim very long error messages
                                        error_msg = error_msg[:200] + "..."
                                    data = json.dumps({"event": "error", "data": error_msg})
                                    yield f"data: {data}\n\n"
                                    raise
                            else:
                                # Unsupported model
                                error_msg = f"Model {model_id} is not supported for streaming"
                                logger.error(error_msg)
                                data = json.dumps({"event": "error", "data": error_msg})
                                yield f"data: {data}\n\n"
                                raise ValueError(error_msg)
                        except AttributeError as attr_error:
                            # Special handling for tuple attribute errors which are common in the streaming code
                            if "tuple" in str(attr_error) and "has no attribute" in str(attr_error):
                                logger.error(f"Tuple attribute error in streaming: {str(attr_error)}")
                                error_msg = "Server streaming error: tuple attribute error. Please use non-streaming mode."
                                data = json.dumps({"event": "error", "data": error_msg})
                                yield f"data: {data}\n\n"
                                raise
                            else:
                                # Re-raise other attribute errors
                                raise
                        
                        # Store assistant response only if we have content
                        if full_response:
                            chat_service.save_streaming_response(conversation, full_response)
                        else:
                            logger.warning("Empty response from streaming API")
                            data = json.dumps({"event": "error", "data": "Empty response from API"})
                            yield f"data: {data}\n\n"
                        
                        # Send event: done
                        data = json.dumps({"event": "done", "data": None})
                        yield f"data: {data}\n\n"
                        
                    except Exception as e:
                        logger.error(f"Error in stream_response generator: {str(e)}")
                        logger.exception(e)  # Log full stack trace
                        
                        # The generator cannot return a response directly, so we need to raise an exception
                        # that can be caught by the outer try/except block
                        raise RuntimeError(f"Stream generator error: {str(e)}")
                        
                        # Stop the generator
                        return
                
                # Start streaming response
                try:
                    # Create the response first
                    response = StreamingHttpResponse(
                        stream_response(),
                        content_type='text/event-stream'
                    )
                    
                    # Explicitly add CORS and other required headers
                    response["Cache-Control"] = "no-cache"
                    response["Connection"] = "keep-alive"
                    response["X-Accel-Buffering"] = "no"  # Disable Nginx buffering
                    
                    # Add CORS headers explicitly here
                    response["Access-Control-Allow-Origin"] = "http://localhost:5174"
                    response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT, DELETE"
                    response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, x-csrftoken, x-api-client"
                    response["Access-Control-Allow-Credentials"] = "true"
                    response["X-Stream-Debug"] = "True"  # Debug header
                    
                    return response
                except Exception as e:
                    logger.error(f"Error creating streaming response: {str(e)}")
                    # Use the helper function to create a properly rendered error response
                    return create_error_response(e)
            
            except Exception as e:
                logger.error(f"Error in streaming setup: {str(e)}")
                # Use the helper function to create a properly rendered error response
                return create_error_response(e)
        
        # Use regular API for non-streaming requests
        else:
            try:
                # Process message using service
                response_data = chat_service.process_message(
                    user_input, 
                    model_id, 
                    request.user,
                    conversation_id,
                    project_id,
                    current_file,
                    is_build_mode
                )
                
                return Response(response_data)
            except Exception as e:
                logger.error(f"Error processing chat message: {str(e)}")
                return create_error_response(e) 