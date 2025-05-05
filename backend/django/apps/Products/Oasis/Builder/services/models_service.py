"""
Service for AI model operations in the Builder app.

This module provides centralized definitions for all AI models used across the application,
ensuring that model information (IDs, names, costs, etc.) is maintained in a single location.
"""

import logging
from typing import List, Tuple, Dict, Any

logger = logging.getLogger(__name__)

# Centralized Model Definitions
MODELS = {
    'claude-3-7-sonnet-20250219': {
        'id': 'claude-3-7-sonnet-20250219',
        'name': 'Claude 3.7 Sonnet',
        'provider': 'anthropic',
        'type': 'anthropic',
        'description': 'Anthropic | High-performance model for complex tasks',
        'capabilities': ['code_generation', 'chat', 'analysis'],
        'maxTokens': 200000,
        'costPerRequest': 0.04,
        'api_version': 'messages'  # Uses Anthropic messages API
    },
    'gpt-4.1': {
        'id': 'gpt-4.1',
        'name': 'GPT-4.1',
        'provider': 'openai',
        'type': 'openai',
        'description': 'OpenAI | Powerful reasoning and creative capability',
        'capabilities': ['code_generation', 'chat', 'analysis'],
        'maxTokens': 128000,
        'costPerRequest': 0.04,
        'api_version': 'chat'  # Uses OpenAI chat completions API
    },
    'gpt-4.1-nano': {
        'id': 'gpt-4.1-nano',
        'name': 'GPT-4.1 Nano',
        'provider': 'openai',
        'type': 'openai',
        'description': 'OpenAI | Fast and cost-effective performance',
        'capabilities': ['code_generation', 'chat', 'analysis'],
        'maxTokens': 128000,
        'costPerRequest': 0.01,
        'api_version': 'chat'  # Uses OpenAI chat completions API
    }
}

# Provider Choices
PROVIDER_CHOICES = [
    ('openai', 'OpenAI'),
    ('anthropic', 'Anthropic'),
]

# Generate MODEL_COSTS from the models for backwards compatibility
MODEL_COSTS = {model_id: model_data['costPerRequest'] for model_id, model_data in MODELS.items()}

# Default model costs for unknown models based on common prefixes
DEFAULT_MODEL_COSTS = {
    'gpt-4.1': 0.04,
    'gpt-4.1-nano': 0.01,
    'claude-3-7-sonnet': 0.04
}

def get_model_choices() -> List[Tuple[str, str]]:
    """
    Get model choices for Django model fields.
    
    Returns:
        list: List of tuples with (id, name) for Django model choices
    """
    return [(model_id, model_data['name']) for model_id, model_data in MODELS.items()]

def get_provider_choices() -> List[Tuple[str, str]]:
    """
    Get provider choices for Django model fields.
    
    Returns:
        list: List of tuples with (id, name) for Django model choices
    """
    return PROVIDER_CHOICES

def get_default_provider() -> str:
    """
    Get the default provider.
    
    Returns:
        str: The default provider ID
    """
    return 'anthropic'

def get_model_by_id(model_id: str) -> dict:
    """
    Get a model definition by its ID.
    
    Args:
        model_id: The model ID to look up
        
    Returns:
        dict: The model definition or None if not found
    """
    return MODELS.get(model_id)

def get_model_cost(model_id: str) -> float:
    """
    Get the cost for a specific model.
    
    Args:
        model_id: The model ID to get the cost for
        
    Returns:
        float: The cost of the model in dollars
    """
    # Get the exact amount from MODEL_COSTS using the model ID directly
    amount = MODEL_COSTS.get(model_id)
    
    # If model not found in MODEL_COSTS, use pattern matching
    if amount is None:
        model_lower = model_id.lower()
        
        if 'claude-3-7-sonnet' in model_lower or 'claude-3-sonnet' in model_lower:
            amount = 0.04
        elif model_lower == 'gpt-4.1' or model_lower.startswith('gpt-4.1-'):
            # Ensure gpt-4.1-nano is handled separately
            if 'nano' in model_lower:
                amount = 0.01
            else:
                amount = 0.04
        else:
            # Default fallback
            amount = 0.04
            
    return amount

def get_available_models() -> list:
    """
    Get a list of all available AI models.
    
    Returns:
        list: List of model definitions
    """
    return list(MODELS.values())

def get_default_model_id() -> str:
    """
    Get the default model ID to use when none is specified.
    
    Returns:
        str: The default model ID
    """
    # Find models with default=True or use the first Claude model
    for model_id, model_data in MODELS.items():
        if model_data.get('provider') == 'anthropic':
            return model_id
    
    # Fallback to any model if no Claude models found
    return next(iter(MODELS.keys()))

def get_model_display_name(model_id: str) -> str:
    """
    Get the display name for a model ID.
    
    Args:
        model_id: The model ID
        
    Returns:
        str: The model display name or the ID if not found
    """
    model = get_model_by_id(model_id)
    return model['name'] if model else model_id

def get_provider_from_model_id(model_id: str) -> str:
    """
    Get the provider for a specific model ID.
    
    Args:
        model_id: The model ID
        
    Returns:
        str: The provider name or 'unknown'
    """
    model = get_model_by_id(model_id)
    return model['provider'] if model else 'unknown'

def get_api_version_from_model_id(model_id: str) -> str:
    """
    Get the API version to use for a model ID.
    
    Args:
        model_id: The model ID
        
    Returns:
        str: The API version ('responses', 'messages', etc.) or None if not found
    """
    model = get_model_by_id(model_id)
    return model.get('api_version') if model else None

def get_models_by_provider(provider: str) -> List[Dict[str, Any]]:
    """
    Get all models for a specific provider.
    
    Args:
        provider: The provider name
        
    Returns:
        list: List of model definitions for the provider
    """
    return [model_data for model_id, model_data in MODELS.items()
            if model_data.get('provider') == provider]


class ModelsService:
    """Service for AI model operations."""
    
    def get_available_models(self):
        """Get a list of all available AI models."""
        return get_available_models()
        
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
            # Import here to avoid circular import
            from apps.Products.Oasis.Agents.services import process_builder_mode_input
            
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
    
    def get_model_by_id(self, model_id):
        """Get a model definition by its ID."""
        return get_model_by_id(model_id)
    
    def get_model_cost(self, model_id):
        """Get the cost for a specific model."""
        return get_model_cost(model_id)
    
    def get_provider_from_model_id(self, model_id):
        """Get the provider for a specific model ID."""
        return get_provider_from_model_id(model_id) 