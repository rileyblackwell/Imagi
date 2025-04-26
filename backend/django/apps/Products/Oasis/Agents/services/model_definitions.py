"""
Centralized model definitions for Imagi Oasis.

This module defines all AI models used across the application, ensuring
that model information (IDs, names, costs, etc.) is maintained in a single location.
"""

import logging

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
        'costPerRequest': 0.04
    },
    'gpt-4.1': {
        'id': 'gpt-4.1',
        'name': 'GPT-4.1',
        'provider': 'openai',
        'type': 'openai',
        'description': 'OpenAI | Powerful reasoning and creative capability',
        'capabilities': ['code_generation', 'chat', 'analysis'],
        'maxTokens': 128000,
        'costPerRequest': 0.04
    },
    'gpt-4.1-nano': {
        'id': 'gpt-4.1-nano',
        'name': 'GPT-4.1 Nano',
        'provider': 'openai',
        'type': 'openai',
        'description': 'OpenAI | Fast and cost-effective performance',
        'capabilities': ['code_generation', 'chat', 'analysis'],
        'maxTokens': 128000,
        'costPerRequest': 0.01
    }
}

# Generate MODEL_COSTS from the models for backwards compatibility
MODEL_COSTS = {model_id: model_data['costPerRequest'] for model_id, model_data in MODELS.items()}

# Default model costs for unknown models based on common prefixes
DEFAULT_MODEL_COSTS = {
    'gpt-4.1': 0.04,
    'gpt-4.1-nano': 0.01,
    'claude-3-7-sonnet': 0.04
}

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