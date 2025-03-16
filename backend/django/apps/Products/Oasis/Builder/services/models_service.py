"""
Service for AI model operations in the Builder app.
"""

import logging

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