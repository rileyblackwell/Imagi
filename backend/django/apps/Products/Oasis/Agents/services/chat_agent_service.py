"""
Chat agent service for Imagi Oasis.

This module provides a specialized agent service for chat-based interactions,
allowing users to have natural language conversations about their web applications.
"""

import logging
import os
from dotenv import load_dotenv
from .agent_service import BaseAgentService
import openai
import anthropic
from apps.Payments.services import PaymentService
from django.utils import timezone

# Load environment variables from .env
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class ChatAgentService(BaseAgentService):
    """
    Specialized agent service for chat-based interactions.
    
    This service handles natural language conversations with users about their
    web applications, providing explanations, suggestions, and guidance.
    """
    
    def __init__(self):
        """Initialize the chat agent service with API keys"""
        super().__init__()
        self.openai_api_key = os.getenv("OPENAI_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_KEY")
        
        # Initialize clients only if keys are available
        self.openai_client = None
        self.anthropic_client = None
        
        if self.openai_api_key:
            self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
        
        if self.anthropic_api_key:
            self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
            
        self.payment_service = PaymentService()
        
        # Log warning if API keys are missing
        if not self.openai_api_key:
            logger.warning("OpenAI API key not found. OpenAI models will not be available.")
        if not self.anthropic_api_key:
            logger.warning("Anthropic API key not found. Anthropic models will not be available.")
    
    def get_system_prompt(self, project_path=None):
        """
        Get the system prompt for chat interactions.
        
        Args:
            project_path (str, optional): The project path for context
            
        Returns:
            dict: A message dictionary with 'role' and 'content' keys
        """
        return {
            "role": "system",
            "content": (
                "You are an expert web designer and developer working within Imagi Oasis, a powerful platform for building web applications. "
                "Your role is to help users understand, design, and improve their web applications through natural conversation.\n\n"
                
                "Key Responsibilities:\n"
                "1. Help users understand their current website structure and design choices.\n"
                "2. Provide clear explanations about Django templates, CSS styling, and web design best practices.\n"
                "3. Suggest improvements and answer questions about the user's web application.\n"
                "4. Maintain context of the entire project while discussing specific files.\n\n"
                
                "Guidelines:\n"
                "1. Always reference the current state of files when discussing them.\n"
                "2. Provide specific, actionable suggestions for improvements.\n"
                "3. Explain technical concepts in a clear, accessible way.\n"
                "4. Consider the entire project context when making recommendations.\n"
                "5. Focus on modern web design principles and best practices.\n\n"
                
                "Remember:\n"
                "- You don't need to prefix your responses with 'As a web development assistant' or similar phrases.\n"
                "- Give direct, practical advice rather than general platitudes.\n"
                "- If you're not sure about something, say so rather than making up information.\n"
                "- Use markdown for formatting when it enhances clarity.\n"
            )
        }

    def get_model_info(self, model_id):
        """
        Get information about the selected model.
        
        Args:
            model_id (str): The ID of the model to use
            
        Returns:
            dict: Information about the model including provider, name, and cost
        """
        model_costs = {
            # OpenAI models
            'gpt-4': {'provider': 'openai', 'cost_per_token': 0.00003, 'output_cost_per_token': 0.00006},
            'gpt-4o': {'provider': 'openai', 'cost_per_token': 0.00002, 'output_cost_per_token': 0.00004},
            'gpt-4o-mini': {'provider': 'openai', 'cost_per_token': 0.00001, 'output_cost_per_token': 0.00002},
            
            # Anthropic models
            'claude-2': {'provider': 'anthropic', 'cost_per_token': 0.00002, 'output_cost_per_token': 0.00006},
            'claude-3-7-sonnet-20250219': {'provider': 'anthropic', 'cost_per_token': 0.00003, 'output_cost_per_token': 0.00015}
        }
        
        return model_costs.get(model_id, {'provider': 'anthropic', 'cost_per_token': 0.00003, 'output_cost_per_token': 0.00015})
    
    def check_user_credits(self, user, model, user_input=None):
        """
        Check if user has enough balance for the selected model.
        
        Args:
            user: The Django user object
            model (str): The AI model to use
            user_input (str, optional): The user input message
            
        Returns:
            tuple: (has_credits, required_amount)
        """
        # Call the parent class method with just user and model
        return super().check_user_credits(user, model)
    
    def deduct_credits(self, user, model, user_input=None):
        """
        Deduct amount from user's account based on model used.
        
        Args:
            user: The Django user object
            model (str): The AI model to use
            user_input (str, optional): The user input message
            
        Returns:
            bool: Success status
        """
        # Call the parent class method with just user and model
        return super().deduct_credits(user, model)
    
    def process_message(self, user_input, model_id, user, conversation_id=None, project_id=None, current_file=None, is_build_mode=False):
        """
        Process a chat message and generate a response.
        
        Args:
            user_input (str): The user's input message
            model_id (str): The model identifier to use
            user (User): The user object
            conversation_id (str, optional): The conversation ID
            project_id (str, optional): The project ID
            current_file (dict, optional): The current file
            is_build_mode (bool, optional): Whether we're in build mode
            
        Returns:
            dict: The response data including the AI's response
        """
        try:
            # Check user credits before proceeding
            has_credits, error = self.check_model_credits(user, model_id)
            if not has_credits:
                return {
                    'success': False,
                    'error': error['error'] if isinstance(error, dict) and 'error' in error else 'Insufficient credits'
                }
            
            # Get or create conversation
            conversation = None
            if conversation_id:
                conversation = self.get_conversation(conversation_id, user)
            
            if not conversation:
                # Get appropriate system prompt based on mode
                system_prompt = self.get_system_prompt()
                if is_build_mode:
                    from .template_agent_service import TemplateAgentService
                    template_agent = TemplateAgentService()
                    system_prompt = template_agent.get_system_prompt()
                    
                conversation = self.create_conversation(user, model_id, system_prompt)
            
            # Add user message to conversation
            self.add_user_message(conversation, user_input, user)
            
            # Get project path from project_id if provided
            project_path = None
            if project_id:
                try:
                    from apps.Products.Oasis.ProjectManager.models import Project
                    project = Project.objects.get(id=project_id, user=user)
                    project_path = project.project_path
                    logger.info(f"Found project path: {project_path}")
                except Exception as e:
                    logger.warning(f"Could not get project path from project_id {project_id}: {str(e)}")
            
            # Build conversation history with project context
            api_messages = self.build_conversation_history(
                conversation,
                project_path=project_path,
                current_file=current_file
            )
            
            # Add project files context if available
            if hasattr(self, 'project_files') and self.project_files:
                logger.info(f"Adding {len(self.project_files)} project files to context")
                project_files_context = "\n\nProject Files:\n"
                for file in self.project_files:
                    file_path = file.get('path', 'unknown')
                    file_type = file.get('type', 'unknown')
                    content = file.get('content', '')
                    if len(content) > 1000:
                        content_preview = content[:1000] + "... (truncated)"
                    else:
                        content_preview = content
                    project_files_context += f"\nFile: {file_path}\nType: {file_type}\nContent:\n{content_preview}\n"
                api_messages.append({
                    'role': 'system',
                    'content': project_files_context
                })
            
            # Add current file information if available
            if current_file:
                current_file_context = f"\n\nCURRENTLY EDITING FILE: {current_file.get('path')}\n"
                if current_file.get('content'):
                    current_file_context += f"\nCurrent Content:\n{current_file.get('content')}\n"
                api_messages.append({
                    'role': 'system',
                    'content': current_file_context
                })
            
            # Generate the response using the appropriate model
            if 'claude' in model_id:
                # Verify anthropic client is available
                if not hasattr(self, 'anthropic_client') or self.anthropic_client is None:
                    logger.error("Anthropic client not available - check API key configuration")
                    return {
                        'success': False,
                        'error': "Anthropic client not initialized - check API key configuration",
                    }
                
                # Get the system message content for Claude
                system_content = ""
                for msg in api_messages:
                    if msg['role'] == 'system':
                        system_content += msg['content'] + "\n\n"
                
                # Filter out system messages for Claude API
                claude_messages = [msg for msg in api_messages if msg['role'] != 'system']
                
                # Make the API call
                completion = self.anthropic_client.messages.create(
                    model=model_id,
                    max_tokens=4096,
                    temperature=0.7,
                    system=system_content.strip(),
                    messages=claude_messages
                )
                response_content = completion.content[0].text
            elif 'gpt' in model_id:
                # Verify OpenAI client is available
                if not hasattr(self, 'openai_client') or self.openai_client is None:
                    logger.error("OpenAI client not available - check API key configuration")
                    return {
                        'success': False,
                        'error': "OpenAI client not initialized - check API key configuration",
                    }
                
                # Make the API call
                completion = self.openai_client.chat.completions.create(
                    model=model_id,
                    messages=api_messages,
                    temperature=0.7,
                    max_tokens=4096
                )
                response_content = completion.choices[0].message.content
            else:
                raise ValueError(f"Unsupported model: {model_id}")
            
            # Validate the response
            is_valid, error = self.validate_response(response_content)
            if not is_valid:
                return {
                    'success': False,
                    'error': error,
                    'response': response_content
                }
            
            # Store the assistant response
            self.add_assistant_message(conversation, response_content, user)
            
            # Deduct credits after successful response
            self.deduct_credits(user, model_id)
            
            # Return the successful response
            return {
                'success': True,
                'conversation_id': str(conversation.id),
                'response': response_content,
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in process_message: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_response(self, content):
        """
        Validate chat response.
        No specific validation needed for chat responses.
        
        Args:
            content (str): The response content to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        return True, None

    def get_conversation(self, conversation_id, user):
        """
        Get a conversation by ID.
        
        Args:
            conversation_id (str): The conversation ID
            user (User): The user object
            
        Returns:
            AgentConversation: The conversation object
            
        Raises:
            Exception: If the conversation is not found
        """
        from ..models import AgentConversation
        try:
            return AgentConversation.objects.get(id=conversation_id, user=user)
        except AgentConversation.DoesNotExist:
            raise Exception("Conversation not found")
    
    def get_conversation_history(self, conversation_id, user):
        """
        Get the conversation history.
        
        Args:
            conversation_id (str): The conversation ID
            user (User): The user object
            
        Returns:
            dict: The conversation history
        """
        from ..models import AgentConversation, AgentMessage
        from ...Agents.api.serializers import AgentMessageSerializer
        
        conversation = self.get_conversation(conversation_id, user)
        messages = AgentMessage.objects.filter(conversation=conversation).order_by('created_at')
        
        serializer = AgentMessageSerializer(messages, many=True)
        return {
            'success': True,
            'conversation_id': conversation_id,
            'messages': serializer.data
        }
    
    def create_conversation(self, user, model_id, system_prompt):
        """
        Create a new conversation.
        
        Args:
            user (User): The user object
            model_id (str): The model identifier
            system_prompt (dict): The system prompt dictionary containing 'content'
            
        Returns:
            AgentConversation: The created conversation
        """
        from ..models import AgentConversation, SystemPrompt
        
        conversation = AgentConversation.objects.create(
            user=user,
            model_name=model_id
        )
        
        # Add system prompt
        SystemPrompt.objects.create(
            conversation=conversation,
            content=system_prompt['content']
        )
        
        return conversation
    
    def add_user_message(self, conversation, content, user):
        """
        Add a user message to a conversation.
        
        Args:
            conversation (AgentConversation): The conversation object
            content (str): The message content
            user (User): The user object
            
        Returns:
            AgentMessage: The created message
        """
        from ..models import AgentMessage
        
        return AgentMessage.objects.create(
            conversation=conversation,
            role='user',
            content=content
        )
    
    def add_assistant_message(self, conversation, content, user):
        """
        Add an assistant message to a conversation.
        
        Args:
            conversation (AgentConversation): The conversation object
            content (str): The message content
            user (User): The user object
            
        Returns:
            AgentMessage: The created message
        """
        from ..models import AgentMessage
        
        return AgentMessage.objects.create(
            conversation=conversation,
            role='assistant',
            content=content
        )
    
    def build_conversation_history(self, conversation, project_path=None, current_file=None):
        """
        Build the conversation history for API requests.
        
        Args:
            conversation (AgentConversation): The conversation object
            project_path (str, optional): The project path
            current_file (dict, optional): The current file
            
        Returns:
            list: The conversation history as a list of messages
        """
        # Import the function from agent_service.py
        from .agent_service import build_conversation_history
        
        # Use the existing function
        return build_conversation_history(conversation, project_path, current_file)
    
    def check_model_credits(self, user, model_id):
        """
        Check if user has enough credits for the selected model.
        
        Args:
            user (User): The Django user object
            model_id (str): The model identifier
            
        Returns:
            tuple: (has_credits, error_response)
            - has_credits: True if user has enough credits, False otherwise
            - error_response: Error dict if validation fails, None otherwise
        """
        from apps.Payments.services.credit_service import CreditService
        from .agent_service import MODEL_COSTS
        
        credit_service = CreditService()
        model_cost = MODEL_COSTS.get(model_id, 0.04)
        
        # Special handling for gpt-4o-mini to ensure correct cost
        if model_id == 'gpt-4o-mini':
            model_cost = 0.005
            logger.info(f"Using fixed cost of $0.005 for gpt-4o-mini regardless of MODEL_COSTS value")
        
        logger.info(f"Model {model_id} cost from MODEL_COSTS: ${model_cost}")
        
        user_balance = credit_service.get_balance(user)
        logger.info(f"User balance for {user.username}: ${user_balance} - Required for {model_id}: ${model_cost}")
        
        # Use an epsilon value to handle floating point precision
        epsilon = 0.0001
        if user_balance + epsilon < model_cost:
            needed_amount = max(0, model_cost - user_balance)
            
            # Special handling for gpt-4o-mini pricing error pattern
            if model_id == 'gpt-4o-mini' and abs(needed_amount - 0.035) < 0.001:
                logger.warning(f"Detected the common gpt-4o-mini pricing error pattern. User has ${user_balance}, needs ${model_cost}, system calculated ${needed_amount} needed")
                logger.warning(f"Allowing this gpt-4o-mini request to proceed despite the error pattern")
                return True, None
            # Only report error if difference is significant (greater than 0.001)
            elif needed_amount > 0.001:
                logger.error(f"Insufficient credits for {user.username}. Has: ${user_balance}, Needs: ${model_cost}, Missing: ${needed_amount}")
                return False, {
                    'success': False,
                    'error': f"Insufficient credits: You need ${needed_amount:.2f} more to use {model_id}. Please add more credits."
                }
            else:
                # If difference is negligible, proceed
                logger.info(f"Negligible credit difference (${needed_amount:.5f}), allowing request to proceed")
                return True, None
        else:
            logger.info(f"User {user.username} has sufficient credits. Balance: ${user_balance}, Required: ${model_cost}")
            return True, None

    def validate_current_file(self, current_file):
        """
        Validate the current file format and required fields.
        
        Args:
            current_file (dict): The current file data
            
        Returns:
            tuple: (is_valid, error_response)
            - is_valid: True if validation succeeds, False otherwise
            - error_response: Error dict if validation fails, None otherwise
        """
        if current_file and not isinstance(current_file, dict):
            logger.error(f"Invalid current_file format: {current_file}")
            return False, {
                'success': False,
                'error': 'current_file must be a dictionary with path, content, and type'
            }
        
        if current_file and isinstance(current_file, dict):
            required_fields = ['path', 'type']
            missing_required = [field for field in required_fields if field not in current_file]
            if missing_required:
                logger.error(f"Missing required fields in current_file: {missing_required}")
                return False, {
                    'success': False,
                    'error': f"current_file must contain {', '.join(required_fields)} fields"
                }
            
            # If content is not provided, we'll fetch it later if needed
            if 'content' not in current_file:
                logger.info(f"current_file missing content field, will be fetched as needed")
        
        return True, None 