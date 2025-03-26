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
    
    def process_message(self, user_input, model_id, user, conversation_id=None, project_path=None, current_file=None, is_build_mode=False):
        """
        Process a chat message and generate a response.
        
        Args:
            user_input (str): The user's input message
            model_id (str): The model identifier to use
            user (User): The user object
            conversation_id (str, optional): The conversation ID
            project_path (str, optional): The project path
            current_file (str, optional): The current file
            is_build_mode (bool, optional): Whether we're in build mode
            
        Returns:
            dict: The response data including the AI's response
        """
        try:
            logger.info(f"Processing message for model {model_id}")
            
            # Check user credits
            has_credits, required_amount = self.check_user_credits(user, model_id, user_input)
            
            if not has_credits:
                logger.warning(f"User {user.username} has insufficient credits for model {model_id}")
                return {
                    'success': False,
                    'error': f"You need {required_amount} more credits to use this model. Please add more credits."
                }
                
            # Create or get conversation
            if conversation_id:
                try:
                    conversation = self.get_conversation(conversation_id, user)
                except Exception as e:
                    logger.error(f"Error getting conversation {conversation_id}: {str(e)}")
                    return {
                        'success': False,
                        'error': f"Error retrieving conversation: {str(e)}"
                    }
            else:
                system_prompt = self.get_system_prompt(project_path)
                conversation = self.create_conversation(user, model_id, system_prompt)
            
            # Add user message
            self.add_user_message(conversation, user_input, user)
            
            # Build conversation history
            messages = self.build_conversation_history(conversation, project_path, current_file)
            
            # Determine the AI provider based on model ID
            provider = 'openai' if 'gpt' in model_id else 'anthropic'
            
            # Generate response based on provider
            try:
                if provider == 'openai':
                    response_content = self.generate_openai_response(messages, model_id)
                else:
                    response_content = self.generate_anthropic_response(messages, model_id)
                    
                # Save the assistant's response
                self.add_assistant_message(conversation, response_content, user)
                
                # Deduct credits
                try:
                    self.deduct_credits(user, model_id)
                except Exception as payment_error:
                    logger.error(f"Error deducting credits: {str(payment_error)}")
                    # Continue anyway as we already generated the response
                
                # Log token usage if available
                # TODO: Implement token usage tracking
                
                # Return the successful response
                return {
                    'success': True,
                    'conversation_id': str(conversation.id),
                    'response': response_content,
                    'timestamp': timezone.now().isoformat()
                }
                
            except Exception as generate_error:
                logger.error(f"Error generating response: {str(generate_error)}")
                return {
                    'success': False,
                    'error': f"Error generating response: {str(generate_error)}"
                }
                
        except Exception as e:
            logger.error(f"Error in process_message: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_openai_stream(self, messages, model_id):
        """
        Generate a streaming response using OpenAI's API.
        
        Args:
            messages (list): List of message dictionaries
            model_id (str): The model ID to use
            
        Returns:
            generator: A streaming response generator
        """
        try:
            if not self.openai_client:
                raise Exception("OpenAI client not initialized")
                
            # Log the call to OpenAI API
            logger.info(f"Calling OpenAI streaming API with model {model_id}")
            
            # Get model configuration
            model_config = self.get_model_info(model_id)
            max_tokens = model_config.get('max_tokens', 4000)
            
            # Create the streamed completion
            return self.openai_client.chat.completions.create(
                model=model_id,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7,
                stream=True
            )
        except Exception as e:
            logger.error(f"Error in OpenAI streaming API: {str(e)}")
            raise

    def _generate_anthropic_stream(self, messages, model_id):
        """
        Generate a streaming response using Anthropic's API.
        
        Args:
            messages (list): List of message dictionaries
            model_id (str): The model ID to use
            
        Returns:
            generator: A streaming response generator
        """
        try:
            if not self.anthropic_client:
                raise Exception("Anthropic client not initialized")
                
            # Log the call to Anthropic API
            logger.info(f"Calling Anthropic streaming API with model {model_id}")
            
            # Convert messages to Anthropic format
            anthropic_messages = []
            system_message = None
            
            for msg in messages:
                if msg['role'] == 'system':
                    system_message = msg['content']
                else:
                    anthropic_messages.append({
                        'role': msg['role'],
                        'content': msg['content']
                    })
            
            # Get model configuration
            model_config = self.get_model_info(model_id)
            max_tokens = model_config.get('max_tokens', 4000)
            
            # Create the streaming message
            return self.anthropic_client.messages.create(
                model=model_id,
                max_tokens=max_tokens,
                messages=anthropic_messages,
                system=system_message,
                stream=True
            )
        except Exception as e:
            logger.error(f"Error in Anthropic streaming API: {str(e)}")
            raise
    
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
    
    def generate_openai_response(self, messages, model_id):
        """
        Generate a response using the OpenAI API.
        
        Args:
            messages (list): The conversation history
            model_id (str): The model identifier
            
        Returns:
            str: The generated response
            
        Raises:
            Exception: If there is an error generating the response
        """
        if not self.openai_client:
            raise Exception("OpenAI client not initialized properly")
        
        try:
            response = self.openai_client.chat.completions.create(
                model=model_id,
                messages=messages,
                temperature=0.7,
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {str(e)}")
            raise
    
    def generate_anthropic_response(self, messages, model_id):
        """
        Generate a response using the Anthropic API.
        
        Args:
            messages (list): The conversation history
            model_id (str): The model identifier
            
        Returns:
            str: The generated response
            
        Raises:
            Exception: If there is an error generating the response
        """
        if not self.anthropic_client:
            raise Exception("Anthropic client not initialized properly")
        
        try:
            # Convert messages to Anthropic format
            system_prompt = None
            anthropic_messages = []
            
            for msg in messages:
                if msg['role'] == 'system':
                    system_prompt = msg['content']
                elif msg['role'] == 'user':
                    anthropic_messages.append({
                        'role': 'user',
                        'content': msg['content']
                    })
                elif msg['role'] == 'assistant':
                    anthropic_messages.append({
                        'role': 'assistant',
                        'content': msg['content']
                    })
            
            response = self.anthropic_client.messages.create(
                model=model_id,
                messages=anthropic_messages,
                system=system_prompt,
                temperature=0.7,
                max_tokens=4096
            )
            
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error generating Anthropic response: {str(e)}")
            raise
    
    def process_message_stream(self, user_input, model_id, user, conversation_id=None, project_path=None, current_file=None):
        """
        Process a chat message with a streaming response.
        
        Args:
            user_input (str): The user's input message
            model_id (str): The model identifier to use
            user (User): The user object
            conversation_id (str, optional): The conversation ID
            project_path (str, optional): The project path
            current_file (str, optional): The current file
            
        Returns:
            tuple: (conversation, api_messages, error_message)
        """
        try:
            logger.info(f"Processing streaming message for model {model_id}")
            
            # Check user credits
            has_credits, required_amount = self.check_user_credits(user, model_id, user_input)
            
            if not has_credits:
                logger.warning(f"User {user.username} has insufficient credits for model {model_id}")
                error_message = f"You need {required_amount} more credits to use this model. Please add more credits."
                return None, None, error_message
                
            # Create or get conversation
            if conversation_id:
                try:
                    conversation = self.get_conversation(conversation_id, user)
                except Exception as e:
                    logger.error(f"Error getting conversation {conversation_id}: {str(e)}")
                    return None, None, f"Error retrieving conversation: {str(e)}"
            else:
                system_prompt = self.get_system_prompt(project_path)
                conversation = self.create_conversation(user, model_id, system_prompt)
            
            # Add user message
            self.add_user_message(conversation, user_input, user)
            
            # Build conversation history
            api_messages = self.build_conversation_history(conversation)
            
            # Deduct credits
            try:
                self.deduct_credits(user, model_id)
            except Exception as e:
                logger.error(f"Error deducting credits: {str(e)}")
                return None, None, f"Error processing payment: {str(e)}"
                
            return conversation, api_messages, None
            
        except Exception as e:
            logger.error(f"Error in process_message_stream: {str(e)}")
            return None, None, str(e)
    
    def save_streaming_response(self, conversation, content):
        """
        Save a streaming response to the database.
        
        Args:
            conversation: The conversation object
            content (str): The content to save
            
        Returns:
            bool: Success status
        """
        try:
            from ..models import AgentMessage
            AgentMessage.objects.create(
                conversation=conversation,
                role='assistant',
                content=content
            )
            logger.info(f"Successfully stored streaming response (length: {len(content)})")
            return True
        except Exception as e:
            logger.error(f"Error saving streaming response to database: {str(e)}")
            logger.exception(e)
            return False

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
    
    def generate_openai_response(self, messages, model_id):
        """
        Generate a response using the OpenAI API.
        
        Args:
            messages (list): The conversation history
            model_id (str): The model identifier
            
        Returns:
            str: The generated response
            
        Raises:
            Exception: If there is an error generating the response
        """
        if not self.openai_client:
            raise Exception("OpenAI client not initialized properly")
        
        try:
            response = self.openai_client.chat.completions.create(
                model=model_id,
                messages=messages,
                temperature=0.7,
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {str(e)}")
            raise
    
    def generate_anthropic_response(self, messages, model_id):
        """
        Generate a response using the Anthropic API.
        
        Args:
            messages (list): The conversation history
            model_id (str): The model identifier
            
        Returns:
            str: The generated response
            
        Raises:
            Exception: If there is an error generating the response
        """
        if not self.anthropic_client:
            raise Exception("Anthropic client not initialized properly")
        
        try:
            # Convert messages to Anthropic format
            system_prompt = None
            anthropic_messages = []
            
            for msg in messages:
                if msg['role'] == 'system':
                    system_prompt = msg['content']
                elif msg['role'] == 'user':
                    anthropic_messages.append({
                        'role': 'user',
                        'content': msg['content']
                    })
                elif msg['role'] == 'assistant':
                    anthropic_messages.append({
                        'role': 'assistant',
                        'content': msg['content']
                    })
            
            response = self.anthropic_client.messages.create(
                model=model_id,
                messages=anthropic_messages,
                system=system_prompt,
                temperature=0.7,
                max_tokens=4096
            )
            
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error generating Anthropic response: {str(e)}")
            raise
    
    def _generate_openai_stream(self, messages, model_id):
        """
        Generate a streaming response using the OpenAI API.
        
        Args:
            messages (list): The conversation history
            model_id (str): The model identifier
            
        Returns:
            Generator: A stream of response chunks
            
        Raises:
            Exception: If there is an error generating the response
        """
        if not self.openai_client:
            raise Exception("OpenAI client not initialized properly")
        
        return self.openai_client.chat.completions.create(
            model=model_id,
            messages=messages,
            temperature=0.7,
            stream=True
        )
    
    def _generate_anthropic_stream(self, messages, model_id):
        """
        Generate a streaming response using the Anthropic API.
        
        Args:
            messages (list): The conversation history
            model_id (str): The model identifier
            
        Returns:
            Generator: A stream of response chunks
            
        Raises:
            Exception: If there is an error generating the response
        """
        if not self.anthropic_client:
            raise Exception("Anthropic client not initialized properly")
        
        # Convert messages to Anthropic format
        system_prompt = None
        anthropic_messages = []
        
        for msg in messages:
            if msg['role'] == 'system':
                system_prompt = msg['content']
            elif msg['role'] == 'user':
                anthropic_messages.append({
                    'role': 'user',
                    'content': msg['content']
                })
            elif msg['role'] == 'assistant':
                anthropic_messages.append({
                    'role': 'assistant',
                    'content': msg['content']
                })
        
        return self.anthropic_client.messages.create(
            model=model_id,
            messages=anthropic_messages,
            system=system_prompt,
            temperature=0.7,
            max_tokens=4096,
            stream=True
        ) 