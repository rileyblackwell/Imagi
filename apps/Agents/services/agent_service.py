import os
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
from ..models import AgentMessage, AgentConversation, SystemPrompt

# Load environment variables from .env
load_dotenv()
openai_key = os.getenv('OPENAI_KEY')
anthropic_key = os.getenv('ANTHROPIC_KEY')

openai_client = OpenAI(api_key=openai_key)
anthropic_client = anthropic.Anthropic(api_key=anthropic_key)

class BaseAgentService:
    """Base class for specialized agent services."""
    
    def __init__(self):
        self.openai_client = openai_client
        self.anthropic_client = anthropic_client
    
    def get_system_prompt(self):
        """
        Get the system prompt for this agent type.
        Should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement get_system_prompt()")
    
    def validate_response(self, content):
        """
        Validate the AI model's response.
        Should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement validate_response()")
    
    def get_additional_context(self, **kwargs):
        """
        Get additional context for the conversation.
        Can be overridden by subclasses to add specific context.
        """
        return None
    
    def process_conversation(self, user_input, model, user, system_prompt_content=None, **kwargs):
        """
        Process a conversation with an AI agent.
        This is the base implementation that specialized services can build upon.
        """
        try:
            # Create new conversation if system prompt is provided
            if system_prompt_content:
                conversation = AgentConversation.objects.create(
                    user=user,
                    model_name=model
                )
                SystemPrompt.objects.create(
                    conversation=conversation,
                    content=system_prompt_content
                )
            else:
                # Get the most recent conversation
                conversation = AgentConversation.objects.filter(
                    user=user
                ).order_by('-created_at').first()
                
                if not conversation:
                    return {
                        'success': False,
                        'error': 'no_active_conversation'
                    }

            # Get conversation history
            messages = AgentMessage.objects.filter(
                conversation=conversation
            ).order_by('created_at')

            # Build messages array for API call
            api_messages = []
            
            # Add system prompt if it exists
            if hasattr(conversation, 'system_prompt'):
                api_messages.append({
                    "role": "system",
                    "content": conversation.system_prompt.content
                })
            else:
                # Use default system prompt from subclass
                api_messages.append(self.get_system_prompt())

            # Add conversation history
            for msg in messages:
                api_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

            # Add additional context if provided by subclass
            additional_context = self.get_additional_context(**kwargs)
            if additional_context:
                api_messages.append({
                    "role": "system",
                    "content": additional_context
                })

            # Add new user message
            api_messages.append({
                "role": "user",
                "content": user_input
            })

            # Make API call based on model
            if model.startswith('claude'):
                # Extract messages for Claude (excluding system messages)
                claude_messages = [
                    msg for msg in api_messages 
                    if msg["role"] != "system"
                ]
                
                # Get system content
                system_content = next(
                    (msg["content"] for msg in api_messages if msg["role"] == "system"),
                    self.get_system_prompt()["content"]
                )
                
                completion = self.anthropic_client.messages.create(
                    model=model,
                    max_tokens=2048,
                    system=system_content,
                    messages=claude_messages
                )
                
                if completion.content:
                    response = completion.content[0].text
                else:
                    raise ValueError("Empty response from Claude API")
            else:
                completion = self.openai_client.chat.completions.create(
                    model=model,
                    messages=api_messages
                )
                response = completion.choices[0].message.content

            # Validate the response using subclass implementation
            is_valid, error_message = self.validate_response(response)
            if not is_valid:
                return {
                    'success': False,
                    'error': error_message,
                    'response': response
                }

            # Save the messages
            AgentMessage.objects.create(
                conversation=conversation,
                role="user",
                content=user_input
            )

            AgentMessage.objects.create(
                conversation=conversation,
                role="assistant",
                content=response
            )

            return {
                'success': True,
                'response': response,
                'conversation_id': conversation.id
            }

        except Exception as e:
            print(f"Error in process_conversation: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            } 