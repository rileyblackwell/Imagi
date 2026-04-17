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
    'gpt-5.4': {
        'id': 'gpt-5.4',
        'name': 'GPT 5.4',
        'provider': 'openai',
        'type': 'openai',
        'description': 'OpenAI | GPT 5.4 for chat and building assistance',
        'capabilities': ['code_generation', 'chat', 'analysis'],
        'maxTokens': 128000,
        'input_price_per_m_tokens': 3,
        'output_price_per_m_tokens': 15,
        'api_version': 'responses',  # Uses OpenAI Responses API
        'supports_temperature': False
    }
}

# Provider Choices
PROVIDER_CHOICES = [
    ('openai', 'OpenAI'),
]

# Generate MODEL_COSTS from the models (token-based pricing: per million tokens)
MODEL_COSTS = {
    model_id: {
        'input': model_data['input_price_per_m_tokens'],
        'output': model_data['output_price_per_m_tokens'],
    }
    for model_id, model_data in MODELS.items()
}

# Default model costs for unknown models (per million tokens)
DEFAULT_MODEL_COSTS = {
    'gpt-5.4': {'input': 3, 'output': 15},
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
    return 'openai'

def get_model_by_id(model_id: str) -> dict:
    """
    Get a model definition by its ID.
    
    Args:
        model_id: The model ID to look up
        
    Returns:
        dict: The model definition or None if not found
    """
    return MODELS.get(model_id)

def model_supports_temperature(model_id: str) -> bool:
    """
    Whether the model supports the 'temperature' parameter.
    Defaults to True when unknown; explicitly False for models that disallow it.
    """
    model = get_model_by_id(model_id)
    if not model:
        return True
    return model.get('supports_temperature', True)

def get_model_cost(model_id: str) -> Dict[str, float]:
    """
    Get the token-based cost for a specific model.

    Args:
        model_id: The model ID to get the cost for

    Returns:
        dict: {'input': price_per_million_input_tokens, 'output': price_per_million_output_tokens}
    """
    amount = MODEL_COSTS.get(model_id)

    if amount is None:
        model_lower = model_id.lower()
        if model_lower.startswith('gpt-5'):
            amount = {'input': 3, 'output': 15}
        else:
            amount = {'input': 3, 'output': 15}

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
    return 'gpt-5.4'

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
            from apps.Products.Imagi.Agents.services import process_builder_mode_input
            
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