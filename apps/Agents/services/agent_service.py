import os
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
from ..models import AgentMessage, AgentConversation, SystemPrompt
from apps.Builder.models import Message

# Load environment variables from .env
load_dotenv()
openai_key = os.getenv('OPENAI_KEY')
anthropic_key = os.getenv('ANTHROPIC_KEY')

openai_client = OpenAI(api_key=openai_key)
anthropic_client = anthropic.Anthropic(api_key=anthropic_key)

def build_conversation_history(conversation):
    """
    Builds a formatted conversation history for the AI model.
    Returns a list of messages in the format expected by the AI APIs.
    """
    messages = []
    
    # Add system prompt if it exists
    if hasattr(conversation, 'system_prompt'):
        messages.append({
            "role": "system",
            "content": conversation.system_prompt.content
        })
    
    # Add conversation history
    history_messages = AgentMessage.objects.filter(
        conversation=conversation
    ).order_by('created_at')
    
    for msg in history_messages:
        messages.append({
            "role": msg.role,
            "content": msg.content
        })
    
    return messages

def format_system_prompt(base_prompt, context=None):
    """
    Formats a system prompt with optional context.
    """
    prompt = base_prompt
    
    if context:
        prompt += f"\n\nCONTEXT:\n{context}"
        
    return {
        "role": "system",
        "content": prompt
    }

def get_last_assistant_message(conversation):
    """
    Gets the most recent assistant message from a conversation.
    """
    return AgentMessage.objects.filter(
        conversation=conversation,
        role='assistant'
    ).order_by('-created_at').first()

def get_conversation_summary(conversation):
    """
    Creates a summary of the conversation including metadata and message count.
    """
    message_count = AgentMessage.objects.filter(conversation=conversation).count()
    system_prompt = getattr(conversation.system_prompt, 'content', None) if hasattr(conversation, 'system_prompt') else None
    
    return {
        'id': conversation.id,
        'model_name': conversation.model_name,
        'created_at': conversation.created_at.isoformat(),
        'message_count': message_count,
        'has_system_prompt': bool(system_prompt),
        'system_prompt_preview': system_prompt[:100] + '...' if system_prompt else None
    }

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
    
    def process_conversation(self, user_input, model, user, system_prompt_content=None, **kwargs):
        """Process a conversation with an AI agent."""
        try:
            # Get or create conversation
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
                conversation = AgentConversation.objects.filter(
                    user=user
                ).order_by('-created_at').first()
                
                if not conversation:
                    return {
                        'success': False,
                        'error': 'no_active_conversation'
                    }

            # Build messages array for API call
            api_messages = []
            
            # 1. Add system prompt (from the specific agent service)
            system_prompt = self.get_system_prompt()
            print("\n=== SYSTEM PROMPT ===")
            print(system_prompt['content'])
            api_messages.append(system_prompt)
            
            # 2. Add project files if available
            project_path = kwargs.get('project_path')
            if project_path:
                print("\n=== PROJECT FILES ===")
                templates_dir = os.path.join(project_path, 'templates')
                css_dir = os.path.join(project_path, 'static', 'css')
                
                # Add HTML files
                if os.path.exists(templates_dir):
                    html_files = [f for f in os.listdir(templates_dir) if f.endswith('.html')]
                    html_files.sort()
                    
                    # Ensure base.html is first, followed by index.html
                    if 'base.html' in html_files:
                        html_files.remove('base.html')
                        html_files.insert(0, 'base.html')
                    if 'index.html' in html_files:
                        html_files.remove('index.html')
                        html_files.insert(1 if 'base.html' in html_files else 0, 'index.html')
                    
                    for filename in html_files:
                        print(f"Adding file: {filename}")
                        file_path = os.path.join(templates_dir, filename)
                        try:
                            with open(file_path, 'r') as f:
                                content = f.read()
                                api_messages.append({
                                    "role": "assistant",
                                    "content": f"[File: {filename}]\n{content}"
                                })
                        except FileNotFoundError:
                            print(f"File not found: {filename}")
                            continue
                
                # Add CSS file
                css_path = os.path.join(css_dir, 'styles.css')
                if os.path.exists(css_path):
                    print("Adding file: styles.css")
                    try:
                        with open(css_path, 'r') as f:
                            content = f.read()
                            api_messages.append({
                                "role": "assistant",
                                "content": f"[File: styles.css]\n{content}"
                            })
                    except FileNotFoundError:
                        print("File not found: styles.css")
            
            # 3. Add conversation history
            messages = AgentMessage.objects.filter(
                conversation=conversation
            ).order_by('created_at')
            
            if messages.exists():
                print("\n=== CONVERSATION HISTORY ===")
                for msg in messages:
                    print(f"[{msg.role.upper()}]: {msg.content[:100]}...")
                    api_messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
            
            # 4. Add current task context
            current_file = kwargs.get('template_name') or kwargs.get('file_name')
            if current_file:
                context_msg = {
                    "role": "system",
                    "content": f"\n=== CURRENT TASK ===\nYou are working on: {current_file}"
                }
                print("\n=== TASK CONTEXT ===")
                print(context_msg['content'])
                api_messages.append(context_msg)
            
            # 5. Add new user message
            api_messages.append({
                "role": "user",
                "content": user_input
            })
            print("\n=== USER INPUT ===")
            print(user_input)

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

            # Log the response
            print("\n=== AI RESPONSE ===")
            print(response)
            print("\n=== END CONVERSATION ===\n")

            # Validate and save messages
            is_valid, error_message = self.validate_response(response)
            if not is_valid:
                return {
                    'success': False,
                    'error': error_message,
                    'response': response
                }

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