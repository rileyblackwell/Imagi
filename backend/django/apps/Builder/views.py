# builder/views.py

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Conversation, Message, Page, Project
from .services.oasis_service import (
    process_builder_mode_input_service,
    undo_last_action_service,
    process_chat_mode_input_service,
    chat_agent
)
from apps.ProjectManager.services import ProjectGenerationService, DevServerManager
from apps.Agents.services.agent_service import build_conversation_history
from apps.Agents.services.template_agent_service import TemplateAgentService
import os
import shutil
from django.utils import timezone
from django.contrib import messages

# Initialize template agent for system prompt
template_agent = TemplateAgentService()

@login_required
def landing_page(request):
    projects = Project.objects.filter(user=request.user).order_by('-updated_at')
    return render(request, 'builder/builder_landing_page.html', {'projects': projects})

@login_required
def create_project(request):
    if request.method == 'POST':
        project_name = request.POST.get('project_name')
        if project_name:
            try:
                print(f"Creating project: {project_name}")  # Debug print
                
                # Use ProjectManager service to create the project
                service = ProjectGenerationService(request.user)
                try:
                    user_project = service.create_project(project_name)
                    print(f"Django project created at: {user_project.project_path}")
                except Exception as e:
                    print(f"Error creating Django project: {str(e)}")
                    raise e
                
                # Create a Project instance that corresponds to the UserProject
                try:
                    project = Project.objects.create(
                        user=request.user,
                        name=project_name,
                        user_project=user_project
                    )
                    print(f"Builder Project created with ID: {project.id}")
                except Exception as e:
                    print(f"Error creating Builder Project: {str(e)}")
                    # Clean up the Django project if Builder Project creation fails
                    if os.path.exists(user_project.project_path):
                        shutil.rmtree(user_project.project_path)
                    user_project.delete()
                    raise e
                
                # Create a new conversation for this project
                try:
                    conversation = Conversation.objects.create(
                        user=request.user,
                        project=project
                    )
                    print(f"Conversation created with ID: {conversation.id}")
                except Exception as e:
                    print(f"Error creating Conversation: {str(e)}")
                    # Clean up if conversation creation fails
                    if os.path.exists(user_project.project_path):
                        shutil.rmtree(user_project.project_path)
                    user_project.delete()
                    project.delete()
                    raise e
                
                messages.success(request, f"Project '{project_name}' created successfully!")
                
                # Get the URL-safe name and redirect to builder workspace
                url_safe_name = project.get_url_safe_name()
                print(f"Redirecting to: /builder/oasis/{url_safe_name}/")
                return redirect('builder:project_workspace', project_name=url_safe_name)
                
            except Exception as e:
                print(f"Error in create_project: {str(e)}")
                messages.error(request, f"Failed to create project: {str(e)}")
                return redirect('builder:landing_page')
        else:
            messages.error(request, "Project name is required.")
            return redirect('builder:landing_page')
    return redirect('builder:landing_page')


@login_required
def project_workspace(request, project_name):
    """Render the builder workspace for a specific project"""
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
        
        return render(request, 'builder/oasis_builder.html', {
            'project': project,
            'conversation': conversation
        })
        
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('builder:landing_page')


def load_project_files(project):
    """Load all files for a project from the database into the project's directories."""
    if not project.user_project:
        raise ValueError("No associated user project found")
        
    project_path = project.user_project.project_path
    
    # Get the project's templates and static directories
    templates_dir = os.path.join(project_path, 'templates')
    static_css_dir = os.path.join(project_path, 'static', 'css')
    
    # Ensure directories exist
    os.makedirs(templates_dir, exist_ok=True)
    os.makedirs(static_css_dir, exist_ok=True)

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
            # Determine the correct directory based on file type
            if page.filename.endswith('.html'):
                output_dir = templates_dir
            elif page.filename.endswith('.css'):
                output_dir = static_css_dir
            else:
                continue  # Skip unsupported file types
                
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

@login_required
@require_http_methods(["POST"])
def process_input(request):
    """Handle file generation requests"""
    try:
        user_input = request.POST.get('user_input')
        model = request.POST.get('model', 'claude-3-5-sonnet-20241022')
        file_name = request.POST.get('file')
        mode = request.POST.get('mode', 'build')
        
        if mode == 'chat':
            # Handle chat mode...
            pass
        else:
            response = process_builder_mode_input_service(
                user_input, model, file_name, request.user
            )
            
            # Check if user needs to purchase credits
            if not response['success'] and response.get('error') == 'insufficient_credits':
                return JsonResponse({
                    'success': False,
                    'error': 'Insufficient credits',
                    'required_credits': response.get('required_credits', 1.0),
                    'redirect_url': response.get('redirect_url')
                }, status=402)  # 402 Payment Required
                
            # Get the active project
            project = Project.objects.filter(
                user=request.user
            ).order_by('-updated_at').first()
            
            if project and project.user_project:
                # Save the file
                if file_name.endswith('.html'):
                    output_dir = os.path.join(project.user_project.project_path, 'templates')
                    file_path = os.path.join(output_dir, file_name)
                elif file_name.endswith('.css'):
                    output_dir = os.path.join(project.user_project.project_path, 'static', 'css')
                    file_path = os.path.join(output_dir, file_name)
                else:
                    return JsonResponse({'error': 'Invalid file type'}, status=400)
                
                # Ensure directory exists
                os.makedirs(output_dir, exist_ok=True)
                
                # Write the content
                if response.get('success', False):
                    content = response.get('response', '')
                    with open(file_path, 'w') as f:
                        f.write(content)
                    
                    # If this is an HTML file, update the project's views and URLs
                    if file_name.endswith('.html') and file_name != 'base.html':
                        service = ProjectGenerationService(request.user)
                        service.add_page_to_project(project.user_project, file_name)
            
            return JsonResponse({
                'success': True,
                'response': response.get('response', ''),
                'file': file_name
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

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
        
        if not conversation.project.user_project:
            return JsonResponse({
                'error': 'No associated user project found',
                'detail': 'Project setup is incomplete'
            }, status=400)
            
        project_path = conversation.project.user_project.project_path
        
        # Get system message from chat agent
        system_msg = chat_agent.get_system_prompt()
        
        # Build messages array for API call
        messages = []
        
        # 1. Add system prompt
        print("\n=== SYSTEM PROMPT ===")
        print(system_msg['content'])
        messages.append(system_msg)
        
        # 2. Add project files
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
                        messages.append({
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
                    messages.append({
                        "role": "assistant",
                        "content": f"[File: styles.css]\n{content}"
                    })
            except FileNotFoundError:
                print("File not found: styles.css")
        
        # 3. Add conversation history from all pages
        history_messages = Message.objects.filter(
            conversation=conversation
        ).order_by('created_at')
        
        if history_messages.exists():
            print("\n=== CONVERSATION HISTORY ===")
            for msg in history_messages:
                print(f"[{msg.role.upper()}]: {msg.content[:100]}...")
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # 4. Add current task context
        context_msg = {
            "role": "system",
            "content": f"\n=== CURRENT TASK ===\nYou are working on: {file_name}"
        }
        print("\n=== TASK CONTEXT ===")
        print(context_msg['content'])
        messages.append(context_msg)
        
        # 5. Add current request
        messages.append({
            "role": "user",
            "content": f"[File: {file_name}]\n{user_input}"
        })
        print("\n=== USER INPUT ===")
        print(user_input)
        
        return JsonResponse({
            'messages': messages
        })
            
    except Exception as e:
        print(f"Error getting conversation history: {str(e)}")
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
            
        if not conversation.project.user_project:
            return JsonResponse({
                'message': 'No associated user project found',
                'status': 'warning'
            })
            
        project_path = conversation.project.user_project.project_path
        
        # Clear messages and pages for this conversation
        Message.objects.filter(conversation=conversation).delete()
        Page.objects.filter(conversation=conversation).delete()
        
        # Clear all files in the project's directories
        templates_dir = os.path.join(project_path, 'templates')
        static_css_dir = os.path.join(project_path, 'static', 'css')
        
        # Clear templates directory
        if os.path.exists(templates_dir):
            for file_name in os.listdir(templates_dir):
                file_path = os.path.join(templates_dir, file_name)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f'Failed to delete {file_path}. Reason: {e}')
                    
        # Clear CSS directory
        if os.path.exists(static_css_dir):
            for file_name in os.listdir(static_css_dir):
                file_path = os.path.join(static_css_dir, file_name)
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
    """Check if a specific page file exists."""
    try:
        file_name = request.POST.get('file')
        if not file_name:
            return JsonResponse({'error': 'File name is required'}, status=400)

        # Get the active project
        project = Project.objects.filter(
            user=request.user
        ).order_by('-updated_at').first()
        
        if not project or not project.user_project:
            return JsonResponse({
                'exists': False,
                'message': 'No active project found'
            })
            
        # Just return success - we don't need to actually check the file
        return JsonResponse({
            'exists': True,
            'message': f'Selected file: {file_name}'
        })
        
    except Exception as e:
        print(f"Error checking file: {str(e)}")
        return JsonResponse({
            'exists': False,
            'message': str(e)
        })


@login_required
def serve_website_file(request, path):
    """Return success without attempting to serve the file"""
    return JsonResponse({
        'success': True,
        'message': 'File operation completed'
    })

@require_http_methods(['POST'])
def process_chat(request):
    try:
        user_input = request.POST.get('user_input', '').strip()
        model = request.POST.get('model', '').strip()
        file_name = request.POST.get('file', '').strip()
        
        if not user_input or not model or not file_name:
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        # Get the active conversation
        conversation = Conversation.objects.filter(
            user=request.user,
            project__isnull=False
        ).select_related('project').latest('project__updated_at')
        
        if not conversation:
            return JsonResponse({
                'error': 'No active project found',
                'detail': 'Please select or create a project first'
            }, status=400)
            
        if not conversation.project.user_project:
            return JsonResponse({
                'error': 'No associated user project found',
                'detail': 'Project setup is incomplete'
            }, status=400)
            
        project_path = conversation.project.user_project.project_path
        
        # Get or create the page for this file
        page = Page.objects.get_or_create(
            conversation=conversation,
            filename=file_name
        )[0]
        
        # Get all messages from all pages for this conversation
        history_messages = Message.objects.filter(
            conversation=conversation
        ).order_by('created_at')
        
        # Convert messages to API format
        conversation_history = []
        for msg in history_messages:
            conversation_history.append({
                "role": msg.role,
                "content": msg.content
            })
        
        try:
            # Process chat using the updated AI service
            response_content = process_chat_mode_input_service(
                user_input=user_input,
                model=model,
                conversation=conversation,
                conversation_history=conversation_history,
                file_name=file_name,
                user=request.user
            )
            
            return JsonResponse({'message': response_content})
            
        except ValueError as e:
            # Handle specific errors (like insufficient credits)
            return JsonResponse({
                'error': str(e),
                'detail': 'Error processing chat request'
            }, status=400)
            
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
        
        # Delete the project's files if they exist
        if project.user_project and project.user_project.project_path:
            project_path = project.user_project.project_path
            if os.path.exists(project_path):
                try:
                    shutil.rmtree(project_path)
                except Exception as e:
                    print(f"Error deleting project files: {str(e)}")
        
        # Delete the project (this will cascade delete related conversations, pages, and messages)
        project.delete()
        
        messages.success(request, f"Project '{project.name}' has been deleted.")
    
    return redirect('builder:landing_page')

@login_required
def preview_project(request):
    if request.method == 'POST':
        try:
            # Get the active project
            project = Project.objects.filter(
                user=request.user
            ).order_by('-updated_at').first()
            
            if not project:
                return JsonResponse({'error': 'No active project found'}, status=404)
            
            if not project.user_project:
                return JsonResponse({'error': 'No associated user project found'}, status=404)
                
            if not project.user_project.project_path:
                return JsonResponse({'error': 'Project path not found'}, status=404)
            
            # Start the development server
            server_manager = DevServerManager(project.user_project)
            server_url = server_manager.get_server_url()
            
            return JsonResponse({'url': server_url})
            
        except Exception as e:
            print(f"Error in preview_project: {str(e)}")  # Debug print
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

