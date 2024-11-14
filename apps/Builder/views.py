# builder/views.py

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Conversation, Message, Page
from .services.oasis_service import process_user_input, test_html, undo_last_action, get_system_message
import os


@login_required
def index(request):
    return render(request, 'builder/oasis_builder.html')


@require_http_methods(['POST'])
def process_input(request):
    user_input = request.POST.get('user_input')
    model = request.POST.get('model')
    page_name = request.POST.get('page')

    if not all([user_input, model, page_name]):
        return JsonResponse({'error': 'Invalid input, model selection, or page.'}, status=400)

    conversation, created = Conversation.objects.get_or_create(user=request.user)
    
    # Get or create the page
    page, created = Page.objects.get_or_create(
        conversation=conversation,
        filename=page_name
    )

    # Process user input for specific page
    html = process_user_input(user_input, model, conversation, page)
    parsed_html = test_html(html)

    # Write the AI-generated HTML to a file
    output_dir = os.path.join(os.path.dirname(__file__), 'website')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, page_name)
    
    with open(output_path, 'w') as f:
        f.write(parsed_html)

    return JsonResponse({'html': parsed_html})


@require_http_methods(['POST'])
def undo_last_action_view(request):
    try:
        conversation = get_object_or_404(Conversation, user=request.user)
        page_name = request.POST.get('page')
        page = get_object_or_404(Page, conversation=conversation, filename=page_name)
        
        previous_html, message = undo_last_action(conversation, page)
        previous_html = test_html(previous_html) if previous_html else ''
        
        output_dir = os.path.join(os.path.dirname(__file__), 'website')
        output_path = os.path.join(output_dir, page_name)
        
        with open(output_path, 'w') as f:
            f.write(previous_html)

        return JsonResponse({'html': previous_html, 'message': message})
    
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
