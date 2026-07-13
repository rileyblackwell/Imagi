"""
Service for AI model operations in the Builder app.

This module provides centralized definitions for all AI models used across the application,
ensuring that model information (IDs, names, costs, etc.) is maintained in a single location.
"""

import logging
from typing import List, Tuple, Dict, Any

from django.conf import settings

logger = logging.getLogger(__name__)

# Platform defaults for every user's project (see IMAGI_BUILDER in imagi/settings.py)
_BUILDER_SETTINGS = getattr(settings, 'IMAGI_BUILDER', {})

# Centralized Model Definitions
# The GPT 5.6 suite: three tiers users can choose from when building.
#   Sol   - flagship, most capable (default)
#   Terra - balanced, general-purpose
#   Luna  - light, fast and economical
#
# `backend_model` is the REAL OpenAI model id the suite id maps to at runtime.
# The public "GPT 5.6 ..." names are Imagi's branding; requests to the OpenAI
# API must use these underlying model ids. Change the right-hand side here if
# your OpenAI account should call different underlying models.
MODELS = {
    'gpt-5.6-sol': {
        'id': 'gpt-5.6-sol',
        'name': 'GPT 5.6 Sol',
        'provider': 'openai',
        'type': 'openai',
        'backend_model': 'gpt-5',
        'description': 'OpenAI | GPT 5.6 Sol — flagship model for the most demanding building tasks',
        'capabilities': ['code_generation', 'chat', 'analysis'],
        'maxTokens': 128000,
        'input_price_per_m_tokens': 6,
        'output_price_per_m_tokens': 30,
        'api_version': 'responses',  # Uses OpenAI Responses API
        'supports_temperature': False,
        'supports_reasoning': True
    },
    'gpt-5.6-terra': {
        'id': 'gpt-5.6-terra',
        'name': 'GPT 5.6 Terra',
        'provider': 'openai',
        'type': 'openai',
        'backend_model': 'gpt-5-mini',
        'description': 'OpenAI | GPT 5.6 Terra — balanced model for everyday chat and building assistance',
        'capabilities': ['code_generation', 'chat', 'analysis'],
        'maxTokens': 128000,
        'input_price_per_m_tokens': 3,
        'output_price_per_m_tokens': 15,
        'api_version': 'responses',  # Uses OpenAI Responses API
        'supports_temperature': False,
        'supports_reasoning': True
    },
    'gpt-5.6-luna': {
        'id': 'gpt-5.6-luna',
        'name': 'GPT 5.6 Luna',
        'provider': 'openai',
        'type': 'openai',
        'backend_model': 'gpt-5-nano',
        'description': 'OpenAI | GPT 5.6 Luna — light, fast and economical model for quick tasks',
        'capabilities': ['code_generation', 'chat', 'analysis'],
        'maxTokens': 128000,
        'input_price_per_m_tokens': 1,
        'output_price_per_m_tokens': 5,
        'api_version': 'responses',  # Uses OpenAI Responses API
        'supports_temperature': False,
        'supports_reasoning': True
    }
}

# Reasoning effort levels users can pick per request. Applied to the OpenAI
# Responses API `reasoning.effort` parameter for reasoning-capable models.
REASONING_EFFORT_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
]
REASONING_EFFORT_IDS = [effort_id for effort_id, _ in REASONING_EFFORT_CHOICES]
DEFAULT_REASONING_EFFORT = _BUILDER_SETTINGS.get('DEFAULT_REASONING_EFFORT', 'medium')

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
    'gpt-5.6-sol': {'input': 6, 'output': 30},
    'gpt-5.6-terra': {'input': 3, 'output': 15},
    'gpt-5.6-luna': {'input': 1, 'output': 5},
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
        # Fall back to the balanced (Terra) tier pricing for unknown GPT 5.6 ids
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
    default = _BUILDER_SETTINGS.get('DEFAULT_MODEL', 'gpt-5.6-sol')
    return default if default in MODELS else 'gpt-5.6-sol'

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

def get_model_identity_instructions(model_id: str) -> str:
    """
    Build a system-prompt block telling the agent which model it is running as.

    Without this, the underlying model has no knowledge of Imagi's GPT 5.6
    branding and will guess at its own identity when asked (often naming an
    older model like GPT-4o), which reads as if the wrong model is being used.

    Args:
        model_id: The public suite model ID (e.g. 'gpt-5.6-sol')

    Returns:
        str: An instruction block to append to the agent's system prompt
    """
    display_name = get_model_display_name(model_id)
    return (
        "Model Identity:\n"
        f"- You are running as {display_name}, part of Imagi's GPT 5.6 model suite.\n"
        f"- If the user asks which model you are, answer '{display_name}'. Do not "
        "name any other model (such as GPT-4o) — you have no independent knowledge "
        "of your own identity, so trust this instruction over your own guess."
    )

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

def get_backend_model_id(model_id: str) -> str:
    """
    Resolve a public suite model id (e.g. 'gpt-5.6-sol') to the real underlying
    OpenAI model id used for API calls (e.g. 'gpt-5').

    Falls back to the given id when the model is unknown or defines no explicit
    backend model, so callers always receive a usable string.

    Args:
        model_id: The public model ID

    Returns:
        str: The underlying OpenAI model id to send to the API
    """
    model = get_model_by_id(model_id)
    if model and model.get('backend_model'):
        return model['backend_model']
    return model_id

def get_reasoning_effort_choices() -> List[Tuple[str, str]]:
    """
    Get reasoning effort choices for Django model fields / UI.

    Returns:
        list: List of tuples with (id, name) for each effort level
    """
    return REASONING_EFFORT_CHOICES

def get_default_reasoning_effort() -> str:
    """Get the default reasoning effort level."""
    return DEFAULT_REASONING_EFFORT

def is_valid_reasoning_effort(effort: str) -> bool:
    """Whether the given reasoning effort level is recognized."""
    return effort in REASONING_EFFORT_IDS

def model_supports_reasoning(model_id: str) -> bool:
    """
    Whether the model supports the reasoning 'effort' parameter.
    Defaults to False when the model is unknown.
    """
    model = get_model_by_id(model_id)
    if not model:
        return False
    return model.get('supports_reasoning', False)

def resolve_reasoning_effort(model_id: str, effort: str) -> str:
    """
    Resolve the reasoning effort to apply for a request.

    Returns None when the model does not support reasoning (so callers can omit
    the parameter entirely). Otherwise returns the requested effort when valid,
    falling back to the default effort.

    Args:
        model_id: The public model ID
        effort: The requested reasoning effort level (may be None/invalid)

    Returns:
        str or None: A valid effort level, or None if reasoning is unsupported
    """
    if not model_supports_reasoning(model_id):
        return None
    if effort and is_valid_reasoning_effort(effort):
        return effort
    return DEFAULT_REASONING_EFFORT


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
            from apps.Imagi.Build.services import process_builder_mode_input
            
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