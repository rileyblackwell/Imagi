"""
Application agent service for Imagi Oasis.

This module provides a specialized agent service for generating complete application 
structures based on user descriptions, handling both frontend and backend components.
"""

import logging
import os
from dotenv import load_dotenv
from .agent_service import BaseAgentService
from ..models import AgentConversation, SystemPrompt, AgentMessage
from django.utils import timezone
import json

# Set up logger
logger = logging.getLogger(__name__)

# Load environment variables from .env
load_dotenv()

class ApplicationAgentService(BaseAgentService):
    """
    Specialized agent service for complete application generation.
    
    This service handles the generation of application structures and scaffolding,
    creating both frontend and backend components based on user requirements.
    """
    
    def get_system_prompt(self):
        """
        Get the base system prompt for the application agent.
        
        Returns:
            dict: System prompt components
        """
        return {
            "base": (
                "You are an expert application builder who understands web application architecture, "
                "frontend frameworks (especially Vue.js), and backend technologies (especially Django). "
                "Your task is to generate complete application structures based on user descriptions.\n\n"
                "When creating applications, you should:\n"
                "1. Think carefully about the architecture and component structure\n"
                "2. Follow modern best practices for the specified technology\n"
                "3. Generate code that is clean, well-structured, and maintainable\n"
                "4. Consider both frontend and backend components\n"
                "5. Design clear API interfaces between frontend and backend"
            ),
            "vue_specific": (
                "For Vue.js applications:\n"
                "- Use Vue 3 with Composition API style\n"
                "- Follow the structure: components/ (with atoms/, molecules/, organisms/), "
                "views/, store/, router/, utils/, services/, types/\n"
                "- Ensure proper TypeScript typing\n"
                "- Implement clean component design with proper props and emit definitions\n"
                "- Use Pinia for state management with proper store structure"
            ),
            "django_specific": (
                "For Django backend:\n"
                "- Use Django REST Framework for API endpoints\n"
                "- Structure with clear separation of views, serializers, models\n"
                "- Implement proper authentication and permissions\n"
                "- Design clean URL patterns organized by functionality\n"
                "- Use Django's ORM effectively with well-designed models"
            )
        }

    def get_additional_context(self, technology='vue', **kwargs):
        """
        Get application-specific context based on technology.
        
        Args:
            technology (str): The technology to use (e.g., 'vue', 'react')
            **kwargs: Additional arguments
            
        Returns:
            str: Additional context for the system prompt
        """
        context = f"You are creating a {technology.title()} application. "
        
        if technology.lower() == 'vue':
            context += "Use Vue 3 with Composition API. Structure your application with proper component hierarchy."
        elif technology.lower() == 'react':
            context += "Use React with functional components and hooks. Follow modern React best practices."
        else:
            context += f"Ensure you follow best practices for {technology}."
            
        return context
    
    def validate_response(self, content):
        """
        Validate application structure response.
        
        Args:
            content (str): The content to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            # Check if content is empty
            if not content or not content.strip():
                logger.error("[ERROR] Application content is empty")
                return False, "Application content is empty"
            
            # Check for at least a few key sections in the response
            required_elements = ['package.json', 'structure', 'component']
            missing_elements = []
            
            for element in required_elements:
                if element.lower() not in content.lower():
                    missing_elements.append(element)
            
            if missing_elements:
                logger.warning(f"[WARNING] Application response is missing elements: {', '.join(missing_elements)}")
                return False, f"Response is missing key elements: {', '.join(missing_elements)}"
            
            # Basic validation checks passed
            return True, None
            
        except Exception as e:
            logger.error(f"[ERROR] Error validating application response: {str(e)}")
            return False, str(e)
    
    def process_application(self, prompt, model, user, project_id, app_name="myapp", technology="vue", conversation_id=None):
        """
        Process a complete application generation request.
        
        Args:
            prompt (str): The user's description of the desired application
            model (str): The AI model to use
            user: The Django user object
            project_id: The ID of the project
            app_name (str): The name of the application
            technology (str): The technology stack to use (e.g., 'vue', 'react')
            conversation_id (int, optional): The ID of an existing conversation
            
        Returns:
            dict: A dictionary containing the result, including the generated application structure
        """
        try:
            # Debug log all input parameters
            logger.info(f"[DEBUG] process_application called with: model={model}, app_name={app_name}, "
                        f"technology={technology}, project_id={project_id}")
            
            # Add technology and project context to the prompt
            project_context = ""
            if project_id:
                # Optional: Get project details to provide more context
                try:
                    from apps.Products.Oasis.ProjectManager.models import Project
                    
                    # Convert project_id to integer if it's a string
                    project_id_int = int(project_id) if isinstance(project_id, str) else project_id
                    
                    logger.info(f"[DEBUG] Looking up project with ID: {project_id_int}")
                    project = Project.objects.get(id=project_id_int)
                    project_context = f"You are creating an application for project '{project.name}' (ID: {project_id}).\n"
                    logger.info(f"[DEBUG] Found project: {project.name}")
                except Exception as e:
                    logger.error(f"[ERROR] Error getting project details: {str(e)}")
                    # Continue without project context
            
            # Get or create conversation
            conversation = None
            if conversation_id:
                try:
                    conversation = AgentConversation.objects.get(id=conversation_id, user=user)
                except AgentConversation.DoesNotExist:
                    logger.warning(f"[WARNING] Conversation {conversation_id} not found for user {user.username}")
                    # Will create a new conversation below
            
            if not conversation:
                conversation = AgentConversation.objects.create(
                    user=user,
                    model_name=model,
                    conversation_type='application'
                )
                logger.info(f"[DEBUG] Created new conversation: {conversation.id}")
                
                # Set up system prompt for the conversation
                system_prompt_content = self.get_system_prompt()['base']
                
                # Add technology-specific guidance
                if technology.lower() == 'vue':
                    system_prompt_content += "\n\n" + self.get_system_prompt()['vue_specific']
                elif technology.lower() == 'django':
                    system_prompt_content += "\n\n" + self.get_system_prompt()['django_specific']
                    
                # Add additional context
                additional_context = self.get_additional_context(technology=technology)
                system_prompt_content += "\n\n" + additional_context
                
                # Create system prompt
                SystemPrompt.objects.create(
                    conversation=conversation,
                    content=system_prompt_content
                )
                logger.info(f"[DEBUG] Added system prompt to conversation")
            
            # Save user message
            user_message = AgentMessage.objects.create(
                conversation=conversation,
                role='user',
                content=f"{project_context}{prompt}\n\nApplication name: {app_name}\nTechnology: {technology}"
            )
            logger.info(f"[DEBUG] Saved user message to conversation")
            
            # Enhanced prompt with requirements for structured output
            enhanced_prompt = (
                f"{project_context}Create a {technology} application with the following description:\n\n"
                f"{prompt}\n\n"
                f"Application name: {app_name}\n"
                f"Technology: {technology}\n\n"
                f"Please provide your response in a structured format that includes:\n"
                f"1. A high-level overview of the application architecture\n"
                f"2. Folder structure and file organization\n"
                f"3. Key components with brief descriptions\n"
                f"4. API endpoints (if applicable)\n"
                f"5. Database schema (if applicable)\n"
                f"You should output production-ready code for key files like package.json, main component files, etc."
            )
            
            # Build the conversation history
            api_messages = []
            
            # Add system prompt if it exists
            system_prompt = SystemPrompt.objects.filter(conversation=conversation).first()
            if system_prompt:
                api_messages.append({
                    "role": "system",
                    "content": system_prompt.content
                })
            
            # Add the user's prompt
            api_messages.append({
                "role": "user",
                "content": enhanced_prompt
            })
            
            # Generate the response using the appropriate model
            logger.info(f"[DEBUG] Generating application with model: {model}")
            
            try:
                if 'claude' in model:
                    if not self.anthropic_client:
                        logger.error("[ERROR] Anthropic client not initialized")
                        return {
                            'success': False,
                            'error': 'Anthropic API not configured'
                        }
                    
                    completion = self.anthropic_client.messages.create(
                        model=model,
                        max_tokens=4096,
                        temperature=0.7,
                        system=api_messages[0]['content'] if api_messages[0]['role'] == 'system' else "",
                        messages=[msg for msg in api_messages if msg['role'] != 'system']
                    )
                    response_content = completion.content[0].text
                    
                elif 'gpt' in model:
                    if not self.openai_client:
                        logger.error("[ERROR] OpenAI client not initialized")
                        return {
                            'success': False,
                            'error': 'OpenAI API not configured'
                        }
                    
                    completion = self.openai_client.chat.completions.create(
                        model=model,
                        messages=api_messages,
                        temperature=0.7,
                        max_tokens=4096
                    )
                    response_content = completion.choices[0].message.content
                    
                else:
                    logger.error(f"[ERROR] Unsupported model: {model}")
                    return {
                        'success': False,
                        'error': f'Unsupported model: {model}'
                    }
                    
            except Exception as api_error:
                logger.error(f"[ERROR] API error: {str(api_error)}")
                return {
                    'success': False,
                    'error': f'API error: {str(api_error)}'
                }
            
            # Save assistant response
            assistant_message = AgentMessage.objects.create(
                conversation=conversation,
                role='assistant',
                content=response_content
            )
            logger.info(f"[DEBUG] Saved assistant response to conversation")
            
            # Validate the response
            is_valid, error = self.validate_response(response_content)
            if not is_valid:
                logger.error(f"[ERROR] Response validation failed: {error}")
                return {
                    'success': False,
                    'error': error,
                    'response': response_content
                }
            
            # Get timestamp for consistency
            current_time = timezone.now().isoformat()
            
            # Process successful generation
            return {
                'success': True,
                'conversation_id': conversation.id,
                'app_name': app_name,
                'technology': technology,
                'response': response_content,
                'timestamp': current_time,
                'user_message': {
                    'id': user_message.id,
                    'role': 'user',
                    'content': prompt,
                    'timestamp': current_time
                },
                'assistant_message': {
                    'id': assistant_message.id,
                    'role': 'assistant',
                    'content': response_content,
                    'timestamp': current_time
                }
            }
                
        except Exception as e:
            import traceback
            logger.error(f"[ERROR] Exception in process_application: {str(e)}")
            logger.error(f"[ERROR] Traceback: {traceback.format_exc()}")
            return {
                'success': False,
                'error': f"Server error in application generation: {str(e)}"
            } 