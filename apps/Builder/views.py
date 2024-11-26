# builder/views.py

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Conversation, Message, Page, Project
from .services.oasis_service import (
    process_user_input, 
    build_conversation_history,
    undo_last_action_service,
    process_chat_input
)
from .services.utils import (
    get_system_message,
    get_file_context,
    ensure_website_directory
)
import os
from django.views.static import serve
from django.utils import timezone
from django.contrib import messages
from django.http import Http404


@login_required
def landing_page(request):
    projects = Project.objects.filter(user=request.user).order_by('-updated_at')
    return render(request, 'builder/builder_landing_page.html', {'projects': projects})

@login_required
def create_project(request):
    if request.method == 'POST':
        project_name = request.POST.get('project_name')
        if project_name:
            project = Project.objects.create(
                user=request.user,
                name=project_name
            )
            # Create a new conversation for this project
            conversation = Conversation.objects.create(
                user=request.user,
                project=project
            )
            
            # Clear and initialize the website directory for the new project
            load_project_files(project)  # This will clear the directory since there are no files yet
            
            # Redirect to the project-specific workspace using URL-safe name
            return redirect('builder:project_workspace', project_name=project.get_url_safe_name())
    return redirect('builder:landing_page')


@login_required
def project_workspace(request, project_name):
    try:
        # Get the project using the URL-safe name
        projects = Project.objects.filter(user=request.user)
        project = None
        
        for p in projects:
            if p.get_url_safe_name() == project_name:
                project = p
                break
        
        if not project:
            messages.error(request, f"Project '{project_name}' not found.")
            return redirect('builder:landing_page')
        
        # Get or create conversation for this project
        conversation, created = Conversation.objects.get_or_create(
            user=request.user,
            project=project
        )
        
        # Update project's last modified time
        project.updated_at = timezone.now()
        project.save()

        # Load project files into website directory
        load_project_files(project)
        
        return render(request, 'builder/oasis_builder.html', {
            'project': project,
            'conversation': conversation
        })
        
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('builder:landing_page')


def load_project_files(project):
    """Load all files for a project from the database into the website directory."""
    output_dir = ensure_website_directory(os.path.dirname(__file__))
    
    # Clear existing files in the directory
    if os.path.exists(output_dir):
        for file in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)

    # Load all pages for this project
    pages = Page.objects.filter(
        conversation__project=project
    ).select_related('conversation')

    # For each page, get the latest content and write to file
    for page in pages:
        latest_message = Message.objects.filter(
            conversation__project=project,
            page=page,
            role='assistant'
        ).order_by('-created_at').first()
        
        if latest_message:
            file_path = os.path.join(output_dir, page.filename)
            with open(file_path, 'w') as f:
                f.write(latest_message.content)


@login_required
def load_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    
    # Get or create a conversation specifically for this project
    conversation, created = Conversation.objects.get_or_create(
        user=request.user,
        project=project
    )
    
    # Update the project's last modified time
    project.updated_at = timezone.now()
    project.save()
    
    # Redirect to the project-specific workspace using URL-safe name
    return redirect('builder:project_workspace', project_name=project.get_url_safe_name())


@login_required
def index(request):
    # This view is deprecated - redirect to landing page
    return redirect('builder:landing_page')

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

        # Get the active conversation for the specific project
        conversation = Conversation.objects.filter(
            user=request.user,
            project__isnull=False
        ).select_related('project').order_by('-project__updated_at').first()
        
        if not conversation:
            return JsonResponse({
                'error': 'No active project found',
                'detail': 'Please select or create a project first'
            }, status=400)
            
        print(f"Processing input for project: {conversation.project.name} (ID: {conversation.project.id})")
        
        # Get or create the page/file
        page, created = Page.objects.get_or_create(
            conversation=conversation,
            filename=file_name
        )

        try:
            # Process user input
            response_content = process_user_input(user_input, model, conversation, page)
            
            # Save the file content to the database
            Message.objects.create(
                conversation=conversation,
                page=page,
                role="assistant",
                content=response_content if isinstance(response_content, str) else response_content.get('html', '')
            )
            
            # Handle different response types
            if isinstance(response_content, dict):
                return JsonResponse(response_content)
            else:
                return JsonResponse({
                    'html': response_content
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
        
        # Get the active conversation for the specific project
        conversation = Conversation.objects.filter(
            user=request.user,
            project__isnull=False
        ).select_related('project').order_by('-project__updated_at').first()
        
        if not conversation:
            return JsonResponse({
                'error': 'No active project found',
                'detail': 'Please select or create a project first'
            }, status=400)
        
        print(f"Getting conversation history for project: {conversation.project.name} (ID: {conversation.project.id})")
        
        # Get or create the page/file
        page, created = Page.objects.get_or_create(
            conversation=conversation,
            filename=file_name
        )
        
        # Get system message
        system_msg = get_system_message()
        
        # Set up output directory
        output_dir = ensure_website_directory(os.path.dirname(__file__))
        
        try:
            # Build conversation history
            conversation_history = build_conversation_history(system_msg, page, output_dir)
            
            # Add file context
            file_context = get_file_context(file_name)
            
            # Add current request
            current_request = f"[File: {file_name}]\n{user_input}"
            
            if model == 'claude-3-5-sonnet-20241022':
                system_content = (
                    f"{system_msg['content']}\n\n"
                    f"CURRENT TASK: You are editing {file_name}\n\n"
                    f"IMPORTANT: Return only the complete, valid file content for {file_name}."
                )
                
                messages = [msg for msg in conversation_history if msg["role"] != "system"]
                messages.append({"role": "user", "content": current_request})
                
                return JsonResponse({
                    "model": "claude-sonnet",
                    "messages": messages,
                    "system": system_content
                })
            else:
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
            print(f"Error building conversation history: {str(e)}")
            return JsonResponse({
                'error': 'Error building conversation history',
                'detail': str(e)
            }, status=500)
            
    except Exception as e:
        print(f"Error in get_conversation_history: {str(e)}")
        return JsonResponse({
            'error': str(e),
            'detail': 'An unexpected error occurred'
        }, status=500)

@require_http_methods(['POST'])
def undo_last_action_view(request):
    try:
        page_name = request.POST.get('page')
        content, message, status_code = undo_last_action_service(request.user, page_name)
        
        response_data = {'message': message}
        if content is not None:
            response_data['html'] = content
                
        return JsonResponse(response_data, status=status_code)
        
    except Exception as e:
        print(f"Error in undo_last_action_view: {str(e)}")
        return JsonResponse({
            'message': 'Nothing to undo'
        }, status=200)

@require_http_methods(['POST'])
def clear_conversation_history(request):
    try:
        # Get the active conversation for the current project
        conversation = Conversation.objects.filter(
            user=request.user,
            project__isnull=False
        ).order_by('-created_at').first()
        
        if not conversation:
            return JsonResponse({
                'message': 'No active project found',
                'status': 'warning'
            })
        
        # Clear messages and pages for this conversation
        Message.objects.filter(conversation=conversation).delete()
        Page.objects.filter(conversation=conversation).delete()
        
        # Clear all files in the website directory
        output_dir = ensure_website_directory(os.path.dirname(__file__))
        if os.path.exists(output_dir):
            for file_name in os.listdir(output_dir):
                file_path = os.path.join(output_dir, file_name)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f'Failed to delete {file_path}. Reason: {e}')
        
        # Reset the project's updated_at timestamp
        conversation.project.updated_at = timezone.now()
        conversation.project.save()
        
        return JsonResponse({
            'message': 'Project history and files cleared successfully',
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
    """Get the content of a specific page file."""
    try:
        file_name = request.POST.get('file')
        if not file_name:
            return JsonResponse({'error': 'File name is required'}, status=400)

        # Get the active conversation
        conversation = Conversation.objects.filter(
            user=request.user,
            project__isnull=False
        ).select_related('project').order_by('-project__updated_at').first()
        
        if not conversation:
            return JsonResponse({'error': 'No active project found'}, status=404)

        # Get or create the page object in the database
        page, created = Page.objects.get_or_create(
            conversation=conversation,
            filename=file_name
        )

        # Get the website directory
        output_dir = ensure_website_directory(os.path.dirname(__file__))
        file_path = os.path.join(output_dir, file_name)
        
        # If the file doesn't exist physically yet, return success with empty content
        # This prevents 404 errors for files that haven't been generated yet
        if not os.path.exists(file_path):
            return JsonResponse({
                'html': '',
                'message': f'Waiting for {file_name} to be generated'
            }, status=200)  # Return 200 instead of 404
            
        # Read and return the file content if it exists
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            return JsonResponse({'html': content})
        except Exception as e:
            print(f"Error reading file {file_name}: {str(e)}")
            return JsonResponse({
                'html': '',
                'message': f'Error reading {file_name}'
            }, status=200)  # Return 200 instead of 404
        
    except Exception as e:
        print(f"Error in get_page: {str(e)}")
        return JsonResponse({
            'html': '',
            'message': str(e)
        }, status=200)  # Return 200 instead of 500


def serve_website_file(request, path):
    """Serve files from the website directory"""
    try:
        # Get the active conversation for the current project
        conversation = Conversation.objects.filter(
            user=request.user,
            project__isnull=False
        ).order_by('-created_at').first()
        
        if not conversation:
            return JsonResponse({
                'error': 'No active project found'
            }, status=404)
        
        # Get the website directory
        website_dir = ensure_website_directory(os.path.dirname(__file__))
        
        # If path is empty or is styles.css, serve index.html
        if not path or path == 'styles.css':
            path = 'index.html'
        
        # Check if the requested file exists
        file_path = os.path.join(website_dir, path)
        if not os.path.exists(file_path):
            raise Http404(f"File {path} not found")
        
        # Serve the file
        return serve(request, path, document_root=website_dir)
        
    except Exception as e:
        print(f"Error serving file: {str(e)}")
        raise Http404("File not found")

@require_http_methods(['POST'])
def process_chat(request):
    try:
        user_input = request.POST.get('user_input', '').strip()
        model = request.POST.get('model', '').strip()
        file_name = request.POST.get('file', '').strip()
        
        if not user_input or not model or not file_name:
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        # Get the active conversation for the specific project using latest updated project
        conversation = Conversation.objects.filter(
            user=request.user,
            project__isnull=False
        ).select_related('project').latest('project__updated_at')
        
        if not conversation:
            return JsonResponse({
                'error': 'No active project found',
                'detail': 'Please select or create a project first'
            }, status=400)
        
        # Get or create the page for this file
        page = Page.objects.get_or_create(
            conversation=conversation,
            filename=file_name
        )[0]
        
        # Get system message
        system_msg = get_system_message()
        
        # Set up output directory
        output_dir = ensure_website_directory(
            os.path.dirname(__file__), 
            conversation.project.id
        )
        
        # Build conversation history with the output directory and page context
        conversation_history = build_conversation_history(system_msg, page, output_dir)
        
        # Process chat using the AI service
        response_content = process_chat_input(user_input, model, conversation, conversation_history, file_name)
        
        return JsonResponse({'message': response_content})
            
    except Exception as e:
        print(f"Error in process_chat: {str(e)}")
        return JsonResponse({
            'error': 'An unexpected error occurred',
            'detail': str(e)
        }, status=500)

@login_required
def delete_project(request, project_id):
    if request.method == 'POST':
        project = get_object_or_404(Project, id=project_id, user=request.user)
        
        # Clear the website directory if this is the current project
        current_conversation = Conversation.objects.filter(
            user=request.user,
            project__isnull=False
        ).order_by('-created_at').first()
        
        if current_conversation and current_conversation.project.id == project_id:
            output_dir = ensure_website_directory(os.path.dirname(__file__))
            if os.path.exists(output_dir):
                for file in os.listdir(output_dir):
                    file_path = os.path.join(output_dir, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
        
        # Delete the project (this will cascade delete related conversations, pages, and messages)
        project.delete()
        
        messages.success(request, f"Project '{project.name}' has been deleted.")
    
    return redirect('builder:landing_page')

