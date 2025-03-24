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
        import traceback
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

@api_view(['GET', 'POST'])
@csrf_exempt
def chat(request):
    """
    API endpoint for chatting with AI agents.
    
    POST: Send a message to the AI agent and get a response.
    Required parameters: message (str), model (str), project_id (str)
    Optional parameters: conversation_id (str), mode (str), current_file (dict), stream (bool)
    
    GET: Retrieve conversation history.
    Required parameter: conversation_id (str)
    """
    # Check authentication
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Log the API call
    logger.info(f"Chat API called by {request.user.username} with method {request.method}")
    
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
            return Response({'error': 'conversation_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get conversation history
            conversation_data = chat_service.get_conversation_history(conversation_id, request.user)
            return Response(conversation_data)
        except Exception as e:
            logger.error(f"Error retrieving conversation: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    
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
            return Response({
                'error': f"Missing required parameters: {', '.join(missing_fields)}",
                'required_fields': ['message', 'model', 'project_id'],
                'provided_fields': {k: v is not None for k, v in {
                    'message': user_input,
                    'model': model_id,
                    'project_id': project_id
                }.items()}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate current_file format if provided
        if current_file and not isinstance(current_file, dict):
            logger.error(f"Invalid current_file format: {current_file}")
            return Response({'error': 'current_file must be a dictionary with path, content, and type'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Check current_file has required fields if provided
        if current_file and isinstance(current_file, dict):
            if not all(key in current_file for key in ['path', 'content', 'type']):
                logger.error(f"Missing required fields in current_file: {current_file.keys()}")
                return Response({'error': 'current_file must contain path, content, and type fields'}, 
                                status=status.HTTP_400_BAD_REQUEST)
        
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
                return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
            
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
                                
                                stream = chat_service._generate_anthropic_stream(api_messages, model_id)
                                
                                # Process the stream
                                with stream as response:
                                    for text in response.text_stream:
                                        # Update full response
                                        full_response += text
                                        
                                        # Send content chunk
                                        data = json.dumps({"event": "content", "data": text})
                                        yield f"data: {data}\n\n"
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
                    logger.error(f"Error in streaming response: {str(e)}")
                    logger.exception(e)  # Log the full stack trace
                    
                    # Try to provide a helpful error message
                    error_msg = str(e)
                    if "tuple" in error_msg and "object has no attribute" in error_msg:
                        error_msg = "Internal server error with message format. Please try again with non-streaming mode."
                    elif len(error_msg) > 200:  # Trim very long error messages
                        error_msg = error_msg[:200] + "..."
                        
                    # Send error event
                    data = json.dumps({"event": "error", "data": error_msg})
                    yield f"data: {data}\n\n"
            
            # Start streaming response
            return StreamingHttpResponse(
                stream_response(),
                content_type='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'X-Accel-Buffering': 'no',  # Disable Nginx buffering
                    'Access-Control-Allow-Origin': '*',  # CORS headers
                }
            )
        
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
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def build_application(request):
    """
    Build a complete application based on a description.
    
    This endpoint accepts a prompt describing the desired application
    and delegates to the application agent service to generate the code structure.
    """
    try:
        # Extract request data
        message = request.data.get('message')
        model = request.data.get('model', 'claude-3-7-sonnet-20250219')
        project_id = request.data.get('project_id')
        app_name = request.data.get('app_name', 'myapp')
        technology = request.data.get('technology', 'vue')  # Default to Vue.js
        conversation_id = request.data.get('conversation_id')
        
        # Debug log the request
        logger.info(f"[INFO] Application build request received: app_name={app_name}, "
                    f"technology={technology}, model={model}, project_id={project_id}")
        
        # Validate required fields
        if not message:
            logger.error("[ERROR] Message is required but was not provided")
            return Response({
                'error': 'Message is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if not project_id:
            logger.error("[ERROR] Project ID is required but was not provided")
            return Response({
                'error': 'Project ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Initialize the application agent service
        from ..services.application_agent_service import ApplicationAgentService
        application_agent = ApplicationAgentService()
            
        # Process the application generation request
        result = application_agent.process_application(
            prompt=message,
            model=model,
            user=request.user,
            project_id=project_id,
            app_name=app_name,
            technology=technology,
            conversation_id=conversation_id
        )
        
        # Return the result from the service
        return Response(result)
            
    except Exception as e:
        import traceback
        logger.error(f"[ERROR] Unhandled exception in build_application view: {str(e)}")
        logger.error(f"[ERROR] Traceback: {traceback.format_exc()}")
        
        # Return error response
        return Response({
            'success': False,
            'error': f"Server error: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 