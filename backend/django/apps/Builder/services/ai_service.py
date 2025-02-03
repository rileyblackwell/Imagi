"""
Service for interacting with AI models.
"""

import os
import logging
from django.conf import settings
from anthropic import Anthropic
import openai

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.anthropic = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        openai.api_key = settings.OPENAI_API_KEY
    
    def generate_code(self, project, prompt, model='claude-3-5-sonnet-20241022', file_path=None):
        """Generate code using the specified AI model."""
        try:
            if 'claude' in model:
                return self._generate_with_anthropic(prompt, model, file_path)
            elif 'gpt' in model:
                return self._generate_with_openai(prompt, model, file_path)
            else:
                raise ValueError(f"Unsupported model: {model}")
        except Exception as e:
            logger.error(f"Error generating code: {str(e)}")
            raise
    
    def _generate_with_anthropic(self, prompt, model, file_path):
        """Generate code using Anthropic's Claude models."""
        try:
            # Prepare the system prompt
            system_prompt = self._get_system_prompt(file_path)
            
            # Make the API call
            response = self.anthropic.messages.create(
                model=model,
                max_tokens=4096,
                temperature=0.7,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return {
                'success': True,
                'content': response.content[0].text,
                'model': model
            }
        except Exception as e:
            logger.error(f"Error with Anthropic API: {str(e)}")
            raise
    
    def _generate_with_openai(self, prompt, model, file_path):
        """Generate code using OpenAI's GPT models."""
        try:
            # Prepare the system prompt
            system_prompt = self._get_system_prompt(file_path)
            
            # Map model names
            model_mapping = {
                'gpt-4o': 'gpt-4',
                'gpt-4o-mini': 'gpt-4-turbo-preview'
            }
            openai_model = model_mapping.get(model)
            
            if not openai_model:
                raise ValueError(f"Invalid OpenAI model: {model}")
            
            # Make the API call
            response = openai.chat.completions.create(
                model=openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4096
            )
            
            return {
                'success': True,
                'content': response.choices[0].message.content,
                'model': model
            }
        except Exception as e:
            logger.error(f"Error with OpenAI API: {str(e)}")
            raise
    
    def _get_system_prompt(self, file_path=None):
        """Get the appropriate system prompt based on the context."""
        base_prompt = """You are an expert web developer assistant helping to build web applications.
You write clean, maintainable, and modern code following best practices.
When generating code, focus on:
1. Modern design patterns and practices
2. Responsive and accessible UI
3. Clean and well-documented code
4. Security best practices
5. Performance optimization"""

        if file_path:
            file_type = os.path.splitext(file_path)[1]
            if file_type == '.html':
                base_prompt += "\nYou are currently working on an HTML template file. Focus on semantic HTML and accessibility."
            elif file_type == '.css':
                base_prompt += "\nYou are currently working on a CSS file. Use modern CSS features and maintain a consistent design system."
            elif file_type == '.js':
                base_prompt += "\nYou are currently working on a JavaScript file. Write clean, modular code with proper error handling."
        
        return base_prompt 