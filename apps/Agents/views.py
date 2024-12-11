from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import json

from .models import AgentConversation, SystemPrompt, AgentMessage
from .services.agent_service import process_agent_conversation
from .services.utils import get_conversation_summary, build_conversation_history


@login_required
@require_http_methods(['POST'])
def create_conversation(request):
    """Create a new conversation with a system prompt."""
    try:
        data = json.loads(request.body)
        model = data.get('model', 'gpt-4')
        system_prompt = data.get('system_prompt')
        
        if not system_prompt:
            return JsonResponse({
                'success': False,
                'error': 'System prompt is required'
            }, status=400)
            
        result = process_agent_conversation(
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
        
        if not user_input:
            return JsonResponse({
                'success': False,
                'error': 'Message content is required'
            }, status=400)
            
        result = process_agent_conversation(
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
