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

def process_agent_conversation(user_input, model, user, system_prompt_content=None):
    """
    Process a conversation with an AI agent, handling message storage.
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

        # Add conversation history
        for msg in messages:
            api_messages.append({
                "role": msg.role,
                "content": msg.content
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
                "You are a helpful AI assistant."
            )
            
            completion = anthropic_client.messages.create(
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
            completion = openai_client.chat.completions.create(
                model=model,
                messages=api_messages
            )
            response = completion.choices[0].message.content

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
        print(f"Error in process_agent_conversation: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        } 