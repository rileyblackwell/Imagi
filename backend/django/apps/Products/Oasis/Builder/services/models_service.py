"""
Service for AI model operations in the Builder app.
"""

import logging
from apps.Products.Oasis.Agents.services import process_builder_mode_input

logger = logging.getLogger(__name__)

class ModelsService:
    """Service for AI model operations."""
    
    def get_available_models(self):
        """Get a list of all available AI models."""
        models = [
            {
                'id': 'claude-3-5-sonnet-20241022',
                'name': 'Claude 3.5 Sonnet',
                'provider': 'anthropic',
                'type': 'anthropic',
                'description': 'Anthropic | High-performance model for complex tasks',
                'capabilities': ['code_generation', 'chat', 'analysis'],
                'maxTokens': 200000,
                'costPerRequest': 0.04
            },
            {
                'id': 'gpt-4o',
                'name': 'GPT-4o',
                'provider': 'openai',
                'type': 'openai',
                'description': 'OpenAI | Powerful reasoning and creative capability',
                'capabilities': ['code_generation', 'chat', 'analysis'],
                'maxTokens': 128000,
                'costPerRequest': 0.04
            },
            {
                'id': 'gpt-4o-mini',
                'name': 'GPT-4o Mini',
                'provider': 'openai',
                'type': 'openai',
                'description': 'OpenAI | Fast and cost-effective performance',
                'capabilities': ['code_generation', 'chat', 'analysis'],
                'maxTokens': 128000,
                'costPerRequest': 0.005
            }
        ]
        return models
        
    def generate_code(self, project, prompt, model, file_content=None):
        """
        Generate code using the specified AI model.
        
        Args:
            project: The project object
            prompt: The user prompt requesting code generation
            model: The AI model ID to use
            file_content: Optional existing file content to consider
            
        Returns:
            dict: Response containing the generated code
        """
        try:
            # Use the process_builder_mode_input function from Agents service
            result = process_builder_mode_input(
                project=project,
                message=prompt,
                model=model,
                file_content=file_content
            )
            return result
        except Exception as e:
            logger.error(f"Error generating code: {str(e)}")
            # Return a graceful error response
            return {
                'error': str(e),
                'code': '',
                'message': f"Failed to generate code: {str(e)}"
            } 