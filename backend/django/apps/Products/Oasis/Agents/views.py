from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import json

from .models import AgentConversation, SystemPrompt, AgentMessage
from .services.template_agent_service import TemplateAgentService
from .services.stylesheet_agent_service import StylesheetAgentService

# Initialize agents
template_agent = TemplateAgentService()
stylesheet_agent = StylesheetAgentService()

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

@login_required
@require_http_methods(['POST'])
def create_conversation(request):
    """Create a new conversation with a system prompt."""
    try:
        data = json.loads(request.body)
        model = data.get('model', 'gpt-4')
        system_prompt = data.get('system_prompt')
        file_type = data.get('file_type', 'html')  # Default to HTML if not specified
        
        if not system_prompt:
            return JsonResponse({
                'success': False,
                'error': 'System prompt is required'
            }, status=400)
        
        # Choose the appropriate agent based on file type
        agent = stylesheet_agent if file_type == 'css' else template_agent
            
        result = agent.process_conversation(
            user_input="Let's begin our conversation.",
            model=model,
            user=request.user,
            system_prompt_content=system_prompt
        )
        
        if result['success']:
            conversation = AgentConversation.objects.get(id=result['conversation_id'])
            return JsonResponse({
                'success': True,
                'conversation': get_conversation_summary(conversation)
            })
        else:
            return JsonResponse(result, status=400)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def list_conversations(request):
    """List all conversations for the current user."""
    conversations = AgentConversation.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    return JsonResponse({
        'success': True,
        'conversations': [
            get_conversation_summary(conv) 
            for conv in conversations
        ]
    })


@login_required
def conversation_detail(request, conversation_id):
    """Get details of a specific conversation."""
    conversation = get_object_or_404(AgentConversation, id=conversation_id, user=request.user)
    messages = build_conversation_history(conversation)
    
    return JsonResponse({
        'success': True,
        'conversation': get_conversation_summary(conversation),
        'messages': messages
    })


@login_required
@require_http_methods(['POST'])
def send_message(request, conversation_id):
    """Send a new message in an existing conversation."""
    try:
        conversation = get_object_or_404(AgentConversation, id=conversation_id, user=request.user)
        data = json.loads(request.body)
        user_input = data.get('message')
        file_type = data.get('file_type', 'html')  # Default to HTML if not specified
        
        if not user_input:
            return JsonResponse({
                'success': False,
                'error': 'Message content is required'
            }, status=400)
        
        # Choose the appropriate agent based on file type
        agent = stylesheet_agent if file_type == 'css' else template_agent
            
        result = agent.process_conversation(
            user_input=user_input,
            model=conversation.model_name,
            user=request.user
        )
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'response': result['response']
            })
        else:
            return JsonResponse(result, status=400)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
