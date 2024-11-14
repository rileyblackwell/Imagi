# builder/views.py

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Conversation, Message, Page
from .services.oasis_service import process_user_input, test_html, undo_last_action, get_system_message
import os
from django.views.static import serve
from django.conf import settings


@login_required
def index(request):
    return render(request, 'builder/oasis_builder.html')


@require_http_methods(['POST'])
def process_input(request):
    # Get and validate input parameters
    user_input = request.POST.get('user_input', '').strip()
    model = request.POST.get('model', '').strip()
    file_name = request.POST.get('file', 'index.html').strip()  # Default to index.html

    # Remove the debug logging for raw POST data
    # print(f"Raw POST data: {dict(request.POST)}")
    
    # Validate required fields
    if not user_input:
        return JsonResponse({'error': 'User input is required'}, status=400)
    if not model:
        return JsonResponse({'error': 'Model selection is required'}, status=400)
    if not file_name:
        file_name = 'index.html'  # Ensure default if somehow empty

    try:
        # Get or create conversation
        conversation, created = Conversation.objects.get_or_create(user=request.user)
        
        # Get or create the page/file
        page, created = Page.objects.get_or_create(
            conversation=conversation,
            filename=file_name
        )

        # Process user input
        response_content = process_user_input(user_input, model, conversation, page)

        # Set up the website directory
        output_dir = os.path.join(os.path.dirname(__file__), 'website')
        os.makedirs(output_dir, exist_ok=True)
        
        if file_name == 'styles.css':
            # Save the CSS file
            css_path = os.path.join(output_dir, 'styles.css')
            with open(css_path, 'w') as f:
                f.write(response_content)
            
            # Get and return the index.html content
            index_path = os.path.join(output_dir, 'index.html')
            if os.path.exists(index_path):
                with open(index_path, 'r') as f:
                    index_content = f.read()
                return JsonResponse({'html': index_content})
            else:
                return JsonResponse({'message': 'CSS file updated successfully, but index.html not found'})
        else:
            # Handle HTML files
            html_path = os.path.join(output_dir, file_name)
            parsed_html = test_html(response_content)
            
            # Ensure the HTML includes a link to styles.css
            if '<link rel="stylesheet" href="styles.css">' not in parsed_html:
                parsed_html = parsed_html.replace('</head>', 
                    '<link rel="stylesheet" href="styles.css">\n</head>')
            
            with open(html_path, 'w') as f:
                f.write(parsed_html)
            return JsonResponse({'html': parsed_html})

    except Exception as e:
        print(f"Error in process_input: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


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
