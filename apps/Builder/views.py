# builder/views.py

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Conversation, Message, Page
from .services.oasis_service import process_user_input, test_html, test_css, undo_last_action, get_system_message
import os
from django.views.static import serve
from django.conf import settings


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
        
        # Get conversation history
        conversation_history = get_conversation_history(conversation, page)
        
        # Return the response
        return JsonResponse({
            'html': response_content,
            'conversation_history': conversation_history
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
            previous_content = test_html(previous_content) if previous_content else ''
            with open(output_path, 'w') as f:
                f.write(previous_content)
            return JsonResponse({'html': previous_content, 'message': message})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['POST'])
def clear_conversation_history(request):
    try:
        # Get the user's conversation
        conversation = get_object_or_404(Conversation, user=request.user)
        
        # Delete all messages and pages
        conversation.messages.all().delete()
        conversation.pages.all().delete()
        
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

def get_conversation_history(conversation, page):
    """Helper function to get the conversation history in a serializable format"""
    # Start with system message
    conversation_history = [get_system_message()]
    
    # Include the most recent content of each page
    all_pages = Page.objects.filter(conversation=conversation)
    
    # First add HTML files
    html_pages = all_pages.exclude(filename='styles.css')
    for html_page in html_pages:
        latest_html = html_page.messages.filter(
            role='assistant'
        ).order_by('-created_at').first()
        
        if latest_html:
            conversation_history.append({
                "role": "assistant",
                "content": f"[File: {html_page.filename}]\nCurrent HTML content:\n{latest_html.content}"
            })
    
    # Then add CSS file
    css_page = all_pages.filter(filename='styles.css').first()
    if css_page:
        latest_css = css_page.messages.filter(
            role='assistant'
        ).order_by('-created_at').first()
        
        if latest_css:
            conversation_history.append({
                "role": "assistant",
                "content": f"[File: styles.css]\nCurrent CSS content:\n{latest_css.content}"
            })
    
    # Add the conversation messages for the current page
    all_messages = conversation.messages.filter(page=page).order_by('created_at')
    
    # Process each message
    for msg in all_messages:
        if msg.role == 'user':
            conversation_history.append({
                "role": "user",
                "content": f"[File: {msg.page.filename}]\n{msg.content}"
            })
        elif msg.role == 'assistant':
            conversation_history.append({
                "role": "assistant",
                "content": f"[File: {msg.page.filename}]\n{msg.content}"
            })
    
    # Add the current file context as the last message
    conversation_history.append({
        "role": "system",
        "content": f"You are now working on file: {page.filename}"
    })
    
    return conversation_history
