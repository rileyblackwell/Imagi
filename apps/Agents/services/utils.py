from ..models import AgentMessage


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