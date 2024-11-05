# builder/views.py

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Conversation, Message
from .services.oasis_service import process_user_input, test_html, undo_last_action, get_system_message
import os


@login_required
def index(request):
    return render(request, 'builder/oasis_builder.html')


@require_http_methods(['POST'])
def process_input(request):
    user_input = request.POST.get('user_input')
    model = request.POST.get('model')

    # Check if input and model are provided
    if not user_input or not model:
        return JsonResponse({'error': 'Invalid input or model selection.'}, status=400)

    # Get or create a conversation for the logged-in user
    conversation, created = Conversation.objects.get_or_create(user=request.user)

    # Process user input
    html = process_user_input(user_input, model, conversation)
    parsed_html = test_html(html)

    # Save user message and assistant response to the database
    Message.objects.create(conversation=conversation, role="user", content=user_input)
    Message.objects.create(conversation=conversation, role="assistant", content=parsed_html)

    # Write the AI-generated HTML to a file (optional for debugging or review)
    output_path = os.path.join(os.path.dirname(__file__), '../../../output.html')
    with open(output_path, 'w') as f:
        f.write(parsed_html)

    return JsonResponse({'html': parsed_html})


@require_http_methods(['POST'])
def undo_last_action_view(request):
    try:
        # Get the user's conversation
        conversation = get_object_or_404(Conversation, user=request.user)
        messages = conversation.messages.all()

        # Undo last user and assistant messages, if available
        if messages.count() >= 2:
            messages.last().delete()  # Delete last assistant message
            messages.last().delete()  # Delete last user message
            message = 'Last action undone successfully.'
        else:
            conversation.messages.all().delete()
            message = 'Not enough history to undo last action; conversation history cleared.'

        # Retrieve the last assistant response if it exists
        previous_html = messages.last().content if messages.exists() else ''
        
        # Write the last HTML response to a file (optional)
        output_path = os.path.join(os.path.dirname(__file__), '../output.html')
        with open(output_path, 'w') as f:
            f.write(previous_html)

        return JsonResponse({'message': message, 'html': previous_html})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['POST'])
def clear_conversation_history(request):
    try:
        # Get the user's conversation and delete all messages
        conversation = get_object_or_404(Conversation, user=request.user)
        conversation.messages.all().delete()
        return JsonResponse({'message': 'Conversation history cleared'})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
