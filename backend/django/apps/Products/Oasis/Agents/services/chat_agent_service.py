"""
Chat agent service for Imagi Oasis.

This module provides a specialized agent service for chat-based interactions,
allowing users to have natural language conversations about their web applications.
"""

import json
import logging
import os
import datetime
from dotenv import load_dotenv
from .agent_service import BaseAgentService
from ..models import AgentConversation, SystemPrompt, AgentMessage
from django.shortcuts import get_object_or_404
import openai
import anthropic
from apps.Payments.services import PaymentService

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
    
    def get_system_prompt(self):
        """
        Get the system prompt for chat interactions.
        
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
            'claude-3-5-sonnet-20241022': {'provider': 'anthropic', 'cost_per_token': 0.00003, 'output_cost_per_token': 0.00015}
        }
        
        return model_costs.get(model_id, {'provider': 'anthropic', 'cost_per_token': 0.00003, 'output_cost_per_token': 0.00015})
    
    def process_message(self, user_input, model_id, user, conversation_id=None, project_path=None):
        """
        Process a chat message and generate a response.
        
        Args:
            user_input (str): The user's message
            model_id (str): The ID of the model to use
            user (User): The Django user making the request
            conversation_id (str, optional): The ID of an existing conversation
            project_path (str, optional): The project path for context
            
        Returns:
            dict: The result of processing the message including the response and metadata
        """
        try:
            # Get model information
            model_info = self.get_model_info(model_id)
            provider = model_info['provider']
            
            # Check if required API client is available
            if provider == 'openai' and not self.openai_client:
                return {
                    'success': False,
                    'error': 'OpenAI API key not configured. Please contact support.'
                }
            elif provider == 'anthropic' and not self.anthropic_client:
                return {
                    'success': False,
                    'error': 'Anthropic API key not configured. Please contact support.'
                }
            
            # Get or create conversation
            if conversation_id:
                try:
                    conversation = AgentConversation.objects.get(id=conversation_id, user=user)
                except AgentConversation.DoesNotExist:
                    return {
                        'success': False,
                        'error': 'Conversation not found'
                    }
            else:
                conversation = AgentConversation.objects.create(
                    user=user,
                    model_name=model_id
                )
                
                # Create system prompt for new conversation
                system_prompt = self.get_system_prompt()
                SystemPrompt.objects.create(
                    conversation=conversation,
                    content=system_prompt['content']
                )
            
            # Add user message to conversation
            timestamp = datetime.datetime.now().isoformat()
            user_message = AgentMessage.objects.create(
                conversation=conversation,
                role='user',
                content=user_input
            )
            
            # Get conversation history
            system_prompt_obj = SystemPrompt.objects.filter(conversation=conversation).first()
            messages = []
            
            # Add system prompt if it exists
            if system_prompt_obj:
                messages.append({"role": "system", "content": system_prompt_obj.content})
            
            # Add previous messages from this conversation
            previous_messages = AgentMessage.objects.filter(conversation=conversation).order_by('created_at')
            for msg in previous_messages:
                messages.append({"role": msg.role, "content": msg.content})
            
            # Generate response based on provider
            if provider == 'openai':
                response_content = self._generate_openai_response(messages, model_id)
            else:  # default to anthropic
                response_content = self._generate_anthropic_response(messages, model_id)
            
            # Save assistant response to database
            assistant_message = AgentMessage.objects.create(
                conversation=conversation,
                role='assistant',
                content=response_content
            )
            
            # Calculate and charge for token usage
            estimated_input_tokens = len(' '.join([msg['content'] for msg in messages])) // 4
            estimated_output_tokens = len(response_content) // 4
            
            total_cost = (
                estimated_input_tokens * model_info['cost_per_token'] +
                estimated_output_tokens * model_info['output_cost_per_token']
            )
            
            # Charge the user for the request
            try:
                self.payment_service.charge_tokens(user, total_cost)
            except Exception as payment_error:
                logger.error(f"Payment error (continuing anyway): {str(payment_error)}")
            
            # Log token usage
            logger.info(f"Token usage: input={estimated_input_tokens}, output={estimated_output_tokens}, cost=${total_cost:.6f}")
            
            # Return the result
            return {
                'success': True,
                'conversation_id': str(conversation.id),
                'response': response_content,
                'timestamp': timestamp
            }
            
        except Exception as e:
            logger.error(f"Error processing chat message: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_openai_response(self, messages, model_id):
        """
        Generate a response using OpenAI's API.
        
        Args:
            messages (list): List of message dictionaries
            model_id (str): The ID of the OpenAI model to use
            
        Returns:
            str: The generated response text
        """
        try:
            response = self.openai_client.chat.completions.create(
                model=model_id,
                messages=messages,
                temperature=0.7,
                max_tokens=2048
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    def _generate_anthropic_response(self, messages, model_id):
        """
        Generate a response using Anthropic's API.
        
        Args:
            messages (list): List of message dictionaries
            model_id (str): The ID of the Anthropic model to use
            
        Returns:
            str: The generated response text
        """
        try:
            # Convert messages to Anthropic format
            system_content = None
            anthropic_messages = []
            
            for message in messages:
                if message['role'] == 'system':
                    system_content = message['content']
                else:
                    anthropic_messages.append({
                        'role': message['role'],
                        'content': message['content']
                    })
            
            # Create the message with Anthropic's API
            response = self.anthropic_client.messages.create(
                model=model_id,
                messages=anthropic_messages,
                system=system_content,
                max_tokens=2048,
                temperature=0.7
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
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