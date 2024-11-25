# builder/views.py

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Conversation, Message, Page
from .services.oasis_service import (
    process_user_input, 
    build_conversation_history,
    undo_last_action,
    process_chat_input
)
from .services.utils import (
    get_system_message,
    get_file_context,
    ensure_website_directory
)
import os
from django.views.static import serve


@login_required
def index(request):
    return render(request, 'builder/oasis_builder.html')


@require_http_methods(['POST'])
def process_input(request):
    try:
        # Get and validate input parameters
        user_input = request.POST.get('user_input', '').strip()
        model = request.POST.get('model', '').strip()
        file_name = request.POST.get('file', 'index.html').strip()
        
        # Validate required fields
        if not user_input:
            return JsonResponse({'error': 'User input is required'}, status=400)
        if not model:
            return JsonResponse({'error': 'Model selection is required'}, status=400)
        if not file_name:
            file_name = 'index.html'

        # Get or create conversation
        conversation = Conversation.objects.get_or_create(user=request.user)[0]
        
        # Get or create the page/file
        page = Page.objects.get_or_create(
            conversation=conversation,
            filename=file_name
        )[0]

        # Process user input
        response_content = process_user_input(user_input, model, conversation, page)
        
        # Handle different response types
        if isinstance(response_content, dict):
            return JsonResponse(response_content)
        else:
            return JsonResponse({
                'html': response_content,
                'conversation_history': response_content.get('conversation_history', {})
            })
            
    except ValueError as e:
        return JsonResponse({
            'error': str(e),
            'detail': 'ValueError occurred during processing'
        }, status=400)
    except Exception as e:
        print(f"Error in process_input: {str(e)}")
        return JsonResponse({
            'error': 'An unexpected error occurred',
            'detail': str(e)
        }, status=500)


@require_http_methods(['POST'])
def get_conversation_history(request):
    try:
        user_input = request.POST.get('user_input', '').strip()
        model = request.POST.get('model', '').strip()
        file_name = request.POST.get('file', 'index.html').strip()
        
        # Get or create conversation
        conversation = Conversation.objects.get_or_create(user=request.user)[0]
        
        # Get or create the page/file
        page = Page.objects.get_or_create(
            conversation=conversation,
            filename=file_name
        )[0]
        
        # Get system message
        system_msg = get_system_message()
        
        # Set up output directory
        output_dir = ensure_website_directory(os.path.dirname(__file__))
        
        # Build conversation history
        conversation_history = build_conversation_history(system_msg, page, output_dir)
        
        # Add file context
        file_context = get_file_context(file_name)
        
        # Add current request
        current_request = f"[File: {file_name}]\n{user_input}"
        
        if model == 'claude-sonnet':
            # For Claude, combine system messages and only show actual messages
            system_content = (
                f"{system_msg['content']}\n\n"
                f"CURRENT TASK: You are editing {file_name}\n\n"
                f"IMPORTANT: Return only the complete, valid file content for {file_name}."
            )
            
            # Only include non-system messages
            messages = [msg for msg in conversation_history if msg["role"] != "system"]
            messages.append({"role": "user", "content": current_request})
            
            return JsonResponse({
                "model": model,
                "messages": messages,
                "system": system_content
            })
        else:
            # For GPT models, include everything
            messages = [
                {"role": "system", "content": system_msg["content"]},
                *conversation_history,
                {"role": "system", "content": file_context},
                {"role": "user", "content": current_request}
            ]
            
            return JsonResponse({
                "model": model,
                "messages": messages
            })
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['POST'])
def undo_last_action_view(request):
    try:
        conversation = get_object_or_404(Conversation, user=request.user)
        page_name = request.POST.get('page')
        page = get_object_or_404(Page, conversation=conversation, filename=page_name)
        
        previous_content, message = undo_last_action(conversation, page)
        
        output_dir = os.path.join(os.path.dirname(__file__), 'website')
        output_path = os.path.join(output_dir, page_name)
        
        if page_name == 'styles.css':
            if previous_content:  # Only write if we have valid previous content
                with open(output_path, 'w') as f:
                    f.write(previous_content)
            # Get and return index.html content
            try:
                with open(os.path.join(output_dir, 'index.html'), 'r') as f:
                    html_content = f.read()
                return JsonResponse({
                    'html': html_content,
                    'message': message
                })
            except FileNotFoundError:
                return JsonResponse({
                    'error': 'Index.html not found',
                    'message': message
                })
        else:
            # Handle HTML files as before
            with open(output_path, 'w') as f:
                f.write(previous_content)
            return JsonResponse({'html': previous_content, 'message': message})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['POST'])
def clear_conversation_history(request):
    try:
        # Try to get the user's conversation
        conversation = Conversation.objects.filter(user=request.user).first()
        
        # If there's no conversation, just clear the website directory and return success
        if not conversation:
            # Clear the website directory
            output_dir = os.path.join(os.path.dirname(__file__), 'website')
            if os.path.exists(output_dir):
                for file_name in os.listdir(output_dir):
                    file_path = os.path.join(output_dir, file_name)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    except Exception as e:
                        print(f'Failed to delete {file_path}. Reason: {e}')
            
            return JsonResponse({
                'message': 'Website files cleared successfully (no conversation history found)',
                'status': 'success'
            })
        
        # If there is a conversation, delete everything
        Message.objects.filter(conversation=conversation).delete()
        Page.objects.filter(conversation=conversation).delete()
        conversation.delete()
        
        # Clear the website directory
        output_dir = os.path.join(os.path.dirname(__file__), 'website')
        if os.path.exists(output_dir):
            for file_name in os.listdir(output_dir):
                file_path = os.path.join(output_dir, file_name)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f'Failed to delete {file_path}. Reason: {e}')
        
        return JsonResponse({
            'message': 'Conversation history and files cleared successfully',
            'status': 'success'
        })
    
    except Exception as e:
        print(f"Error in clear_conversation_history: {str(e)}")
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)


@require_http_methods(['POST'])
def get_page(request):
    try:
        file_name = request.POST.get('file')
        if not file_name:
            return JsonResponse({'error': 'File name is required'}, status=400)

        output_dir = os.path.join(os.path.dirname(__file__), 'website')
        file_path = os.path.join(output_dir, file_name)
        
        if not os.path.exists(file_path):
            return JsonResponse({'error': 'File not found'}, status=404)
            
        with open(file_path, 'r') as f:
            content = f.read()
            
        return JsonResponse({'html': content})
        
    except Exception as e:
        print(f"Error in get_page: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


def serve_website_file(request, path):
    """Serve files from the website directory"""
    website_dir = os.path.join(os.path.dirname(__file__), 'website')
    if not os.path.exists(website_dir):
        os.makedirs(website_dir)
    return serve(request, path, document_root=website_dir)


@require_http_methods(['POST'])
def process_chat(request):
    try:
        user_input = request.POST.get('user_input', '').strip()
        model = request.POST.get('model', '').strip()
        
        if not user_input or not model:
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        # Get or create conversation
        conversation = Conversation.objects.get_or_create(user=request.user)[0]
        
        # Get system message
        system_msg = get_system_message()
        
        # Set up output directory
        output_dir = ensure_website_directory(os.path.dirname(__file__))
        
        # Build conversation history with the output directory
        conversation_history = build_conversation_history(system_msg, None, output_dir)
        
        # Process chat using the AI service
        response_content = process_chat_input(user_input, model, conversation, conversation_history)
        
        return JsonResponse({'message': response_content})
            
    except Exception as e:
        print(f"Error in process_chat: {str(e)}")
        return JsonResponse({
            'error': 'An unexpected error occurred',
            'detail': str(e)
        }, status=500)
