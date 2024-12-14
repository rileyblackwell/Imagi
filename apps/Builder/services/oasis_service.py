# builder/services/oasis_service.py

import os
from dotenv import load_dotenv
from django.urls import reverse
from django.db.models import F
from ..models import Message, Conversation, Page
from apps.Agents.services.template_agent_service import TemplateAgentService
from apps.Agents.services.stylesheet_agent_service import StylesheetAgentService
from apps.Agents.models import AgentConversation

# Load environment variables from .env
load_dotenv()

# Initialize agents
template_agent = TemplateAgentService()
stylesheet_agent = StylesheetAgentService()

# Add model costs constants
MODEL_COSTS = {
    'claude-3-5-sonnet-20241022': 0.10,  # $0.10 per request
    'gpt-4': 0.10,  # $0.10 per request
    'gpt-4-mini': 0.005  # $0.005 per request
}

def check_user_credits(user, model):
    """Check if user has enough balance for the selected model."""
    try:
        profile = user.profile
        required_amount = MODEL_COSTS.get(model, 0.10)
        
        if profile.balance < required_amount:
            return False, required_amount
        return True, required_amount
    except Exception as e:
        print(f"Error checking user balance: {str(e)}")
        return False, 0.10

def deduct_credits(user, model):
    """Deduct amount from user's account based on model used."""
    try:
        profile = user.profile
        amount_to_deduct = MODEL_COSTS.get(model, 0.10)
        profile.balance = F('balance') - amount_to_deduct
        profile.save(update_fields=['balance'])
        
        # Refresh from database to get the new value
        profile.refresh_from_db()
        return True
    except Exception as e:
        print(f"Error deducting amount: {str(e)}")
        return False

def get_active_conversation(user):
    """Retrieve the active conversation for the user."""
    conversation = Conversation.objects.filter(
        user=user,
        project__isnull=False
    ).select_related('project').order_by('-project__updated_at').first()
    
    if not conversation:
        raise ValueError('No active project found. Please select or create a project first.')
    
    return conversation

def process_builder_mode_input_service(user_input, model, file_name, user):
    """
    Handles all business logic for processing user input and generating website content.
    """
    try:
        # Check if user has enough credits
        has_credits, required_credits = check_user_credits(user, model)
        if not has_credits:
            return {
                'success': False,
                'error': 'insufficient_credits',
                'required_credits': required_credits,
                'redirect_url': reverse('payments:create-checkout-session')
            }

        print(f"Processing builder mode input: {user_input}")
        # Validate required fields
        if not user_input or not user_input.strip():
            raise ValueError('User input cannot be empty')
        if not model:
            raise ValueError('Model selection is required')
        if not file_name:
            raise ValueError('File selection is required')

        # Get the active conversation for the specific project
        conversation = get_active_conversation(user)
        
        if not conversation.project.user_project:
            raise ValueError("No associated user project found")
            
        # Get or create the page/file
        page, created = Page.objects.get_or_create(
            conversation=conversation,
            filename=file_name
        )

        # Get or create an agent conversation
        agent_conversation = AgentConversation.objects.filter(
            user=user
        ).order_by('-created_at').first()

        # Choose the appropriate agent based on file type
        agent = stylesheet_agent if file_name.endswith('.css') else template_agent

        if not agent_conversation:
            # Create initial system prompt based on file type
            initial_prompt = agent.get_system_prompt()['content']

            # Create new agent conversation with initial system prompt
            init_result = agent.process_conversation(
                user_input="Initialize conversation",
                model=model,
                user=user,
                system_prompt_content=initial_prompt
            )
            if not init_result['success']:
                raise ValueError(init_result.get('error', 'Failed to initialize agent conversation'))

        # Get project paths
        project_path = conversation.project.user_project.project_path
        templates_dir = os.path.join(project_path, 'templates')
        static_css_dir = os.path.join(project_path, 'static', 'css')
        
        # Ensure directories exist
        os.makedirs(templates_dir, exist_ok=True)
        os.makedirs(static_css_dir, exist_ok=True)

        # Build conversation history with all project files
        api_messages = []
        
        # 1. Add system prompt
        system_prompt = agent.get_system_prompt()
        api_messages.append(system_prompt)
        
        # 2. Add all project files
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
                file_path = os.path.join(templates_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        api_messages.append({
                            "role": "assistant",
                            "content": f"[File: {filename}]\n{content}"
                        })
                except FileNotFoundError:
                    continue
        
        # Add CSS file
        css_path = os.path.join(static_css_dir, 'styles.css')
        if os.path.exists(css_path):
            try:
                with open(css_path, 'r') as f:
                    content = f.read()
                    api_messages.append({
                        "role": "assistant",
                        "content": f"[File: styles.css]\n{content}"
                    })
            except FileNotFoundError:
                pass
        
        # 3. Add conversation history
        history_messages = Message.objects.filter(
            conversation=conversation,
            page=page
        ).order_by('created_at')
        
        for msg in history_messages:
            api_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # 4. Add current task context
        api_messages.append({
            "role": "system",
            "content": f"\n=== CURRENT TASK ===\nYou are working on: {file_name}"
        })

        # 5. Add current request with enhanced instructions
        if file_name.endswith('.html'):
            enhanced_input = f"""
Please generate a complete Django template following these requirements:
1. Include {{% load static %}} at the top
2. Use proper Django template syntax
3. Follow responsive design principles
4. Maintain consistent indentation
5. Include all necessary template blocks

User request: {user_input}
"""
        else:
            enhanced_input = user_input

        api_messages.append({
            "role": "user",
            "content": enhanced_input
        })

        # Make API call based on file type
        if file_name.endswith('.css'):
            result = stylesheet_agent.process_conversation(
                user_input=enhanced_input,
                model=model,
                user=user,
                project_path=project_path,
                file_name=file_name,
                messages=api_messages,
                use_provided_messages=True  # Tell agent to use our messages
            )
        else:
            result = template_agent.process_conversation(
                user_input=enhanced_input,
                model=model,
                user=user,
                project_path=project_path,
                template_name=file_name,
                messages=api_messages,
                use_provided_messages=True  # Tell agent to use our messages
            )

        # Get response and handle validation
        response = result.get('response', '')
        if not result['success']:
            print(f"Warning: {result.get('error', 'Unknown validation error')}")
            
            # For HTML templates, try to fix common issues
            if file_name.endswith('.html'):
                # Add missing {% load static %} if needed
                if '{{% load static %}}' not in response:
                    response = '{{% load static %}}\n' + response
                
                # Ensure DOCTYPE and HTML structure for base.html
                if file_name == 'base.html' and '<!DOCTYPE html>' not in response:
                    response = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{% block title %}}{{% endblock %}}</title>
    {{% block extra_css %}}{{% endblock %}}
</head>
<body>
    {{% block content %}}{{% endblock %}}
    {{% block extra_js %}}{{% endblock %}}
</body>
</html>"""
                
                # Validate the fixed template
                is_valid, error_msg = template_agent.validate_response(response)
                if is_valid:
                    result['success'] = True
                    result['response'] = response
                    print("Template fixed successfully")
            
            if not result['success']:
                # If it's still a validation error, we'll return the response anyway
                if 'Missing' in result.get('error', '') or 'Mismatched' in result.get('error', ''):
                    # Save messages to database
                    Message.objects.create(
                        conversation=conversation,
                        page=page,
                        role="user",
                        content=user_input
                    )

                    Message.objects.create(
                        conversation=conversation,
                        page=page,
                        role="assistant",
                        content=response
                    )

                    # Deduct credits since we're using the response
                    if not deduct_credits(user, model):
                        raise ValueError("Failed to deduct credits")

                    return {
                        'success': True,
                        'response': response,
                        'file': file_name,
                        'warning': result.get('error')  # Include the validation error as a warning
                    }
                else:
                    # For non-validation errors, raise the error
                    raise ValueError(result.get('error', 'Error processing request'))

        # Save messages to database
        Message.objects.create(
            conversation=conversation,
            page=page,
            role="user",
            content=user_input
        )

        Message.objects.create(
            conversation=conversation,
            page=page,
            role="assistant",
            content=response
        )

        # Save the generated content to the appropriate file
        if file_name.endswith('.html'):
            output_path = os.path.join(templates_dir, file_name)
        else:
            output_path = os.path.join(static_css_dir, file_name)
            
        with open(output_path, 'w') as f:
            f.write(response)
        print(f"Saved generated content to: {output_path}")

        # If we get here, the request was successful, so deduct credits
        if not deduct_credits(user, model):
            raise ValueError("Failed to deduct credits")

        # Return the content in a consistent format
        return {
            'success': True,
            'response': response,
            'file': file_name
        }
            
    except Exception as e:
        print(f"Error in process_builder_mode_input_service: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def undo_last_action_service(user, page_name):
    """
    Service function to handle the business logic for undoing the last action.
    Returns a tuple of (content, message, status_code)
    """
    try:
        # Get the active conversation
        conversation = Conversation.objects.filter(
            user=user,
            project__isnull=False
        ).order_by('-created_at').first()
        
        if not conversation or not page_name:
            return None, 'Nothing to undo', 200
            
        # Try to get the page
        try:
            page = Page.objects.get(conversation=conversation, filename=page_name)
        except Page.DoesNotExist:
            return None, 'Nothing to undo', 200
        
        # Get previous content
        messages = Message.objects.filter(
            conversation=conversation,
            page=page,
            role='assistant'
        ).order_by('-created_at')
        
        if messages.count() < 2:
            return None, 'Nothing to undo', 200
        
        # Get the previous version (second most recent)
        previous_content = messages[1].content if messages.count() > 1 else ''
        
        if not previous_content:
            return None, 'Nothing to undo', 200
        
        # Delete the most recent version
        messages[0].delete()
        
        # Get the project path and determine the correct output directory
        project_path = conversation.project.user_project.project_path
        if page_name.endswith('.html'):
            output_dir = os.path.join(project_path, 'templates')
        elif page_name.endswith('.css'):
            output_dir = os.path.join(project_path, 'static', 'css')
        else:
            return None, 'Invalid file type', 400
            
        # Write the previous content to file
        output_path = os.path.join(output_dir, page_name)
        with open(output_path, 'w') as f:
            f.write(previous_content)
        
        # For CSS files, we need to return the HTML content to re-render the page
        if page_name == 'styles.css':
            try:
                index_path = os.path.join(project_path, 'templates', 'index.html')
                with open(index_path, 'r') as f:
                    html_content = f.read()
                return html_content, 'Previous version restored', 200
            except FileNotFoundError:
                return previous_content, 'Previous version restored', 200
        else:
            return previous_content, 'Previous version restored', 200
            
    except Exception as e:
        print(f"Error in undo_last_action_service: {str(e)}")
        return None, 'Nothing to undo', 200

def process_chat_mode_input_service(user_input, model, conversation, conversation_history, file_name, user):
    """Processes chat input without generating website files."""
    try:
        # Check if user has enough credits
        has_credits, required_credits = check_user_credits(user, model)
        if not has_credits:
            raise ValueError(f"Insufficient credits. Required: ${required_credits}")

        # Get or create the page for this file
        page, created = Page.objects.get_or_create(
            conversation=conversation,
            filename=file_name
        )

        # Get or create an agent conversation
        agent_conversation = AgentConversation.objects.filter(
            user=user
        ).order_by('-created_at').first()

        if not agent_conversation:
            # Create initial system prompt based on file type
            if file_name.endswith('.css'):
                initial_prompt = stylesheet_agent.get_system_prompt()['content']
            else:
                initial_prompt = template_agent.get_system_prompt()['content']

            # Create new agent conversation with initial system prompt
            result = (stylesheet_agent if file_name.endswith('.css') else template_agent).process_conversation(
                user_input="Initialize conversation",
                model=model,
                user=user,
                system_prompt_content=initial_prompt
            )
            if not result['success']:
                raise ValueError(result.get('error', 'Failed to initialize agent conversation'))

        # Choose the appropriate agent based on file type
        if file_name.endswith('.css'):
            result = stylesheet_agent.process_conversation(
                user_input=f"[Chat Mode] {user_input}",
                model=model,
                user=user
            )
        else:
            result = template_agent.process_conversation(
                user_input=f"[Chat Mode] {user_input}",
                model=model,
                user=user,
                template_name=file_name
            )

        # Even if validation fails, we want to return the response
        response = result.get('response', '')
        if not result['success']:
            print(f"Warning: {result.get('error', 'Unknown validation error')}")
            # For chat mode, we don't need to validate the response
            if 'Missing' in result.get('error', '') or 'Mismatched' in result.get('error', ''):
                # Save the chat messages anyway
                Message.objects.create(
                    conversation=conversation,
                    page=page,
                    role="user",
                    content=f"[Chat][File: {file_name}]\n{user_input}"
                )

                Message.objects.create(
                    conversation=conversation,
                    page=page,
                    role="assistant",
                    content=f"[Chat][File: {file_name}]\n{response}"
                )

                # Deduct credits since we're using the response
                if not deduct_credits(user, model):
                    raise ValueError("Failed to deduct credits")

                return response
            else:
                # For non-validation errors, raise the error
                raise ValueError(result.get('error', 'Error processing request'))

        # Save the chat messages to the conversation
        Message.objects.create(
            conversation=conversation,
            page=page,
            role="user",
            content=f"[Chat][File: {file_name}]\n{user_input}"
        )

        Message.objects.create(
            conversation=conversation,
            page=page,
            role="assistant",
            content=f"[Chat][File: {file_name}]\n{response}"
        )

        # Deduct credits after successful API call
        if not deduct_credits(user, model):
            raise ValueError("Failed to deduct credits")

        return response

    except Exception as e:
        raise ValueError(str(e))
