"""
Service for AI model operations in the Builder app.

This module provides centralized definitions for all AI models used across the application,
ensuring that model information (IDs, names, costs, etc.) is maintained in a single location.
"""

from typing import List, Tuple

from django.conf import settings

# Platform defaults for every user's project (see IMAGI_BUILDER in imagi/settings.py)
_BUILDER_SETTINGS = getattr(settings, 'IMAGI_BUILDER', {})

# Centralized Model Definitions
# Two generations users can choose from when building.
#   GPT 6 Astra - frontier tier, 1M-token context, priciest by a wide margin
#   The GPT 5.6 suite:
#     Sol   - flagship of the 5.6 generation
#     Terra - balanced, general-purpose (default)
#     Luna  - light, fast and economical
#
# `backend_model` is the REAL OpenAI model id a public id maps to at runtime.
# The public "GPT 5.6 ..." names are Imagi's branding; requests to the OpenAI
# API must use these underlying model ids. Change the right-hand side here if
# your OpenAI account should call different underlying models. (Astra is the
# exception where branding and the real id coincide: OpenAI ships it as
# `gpt-6-astra` and we surface it under that name.)
#
# `reasoning_efforts` is the ladder each model actually accepts — it is NOT the
# same for every model, so it is spelled out per entry rather than defaulted.
MODELS = {
    'gpt-6-astra': {
        'id': 'gpt-6-astra',
        'name': 'GPT 6 Astra',
        'provider': 'openai',
        'type': 'openai',
        'backend_model': 'gpt-6-astra',
        'description': 'OpenAI | GPT 6 Astra — frontier model for the hardest building work, with a 1M-token context',
        'capabilities': ['code_generation', 'chat', 'analysis'],
        'maxTokens': 1000000,
        # Retail, marked up over OpenAI's $10/$50 list price (see Payments'
        # plans.py). NOTE: OpenAI charges 2x input / 1.5x output on requests
        # over 272k input tokens; compute_cost_usd bills one flat rate, so a
        # very long-context Astra run earns thinner margin than a short one.
        'input_price_per_m_tokens': 20,
        'output_price_per_m_tokens': 100,
        'api_version': 'responses',  # Uses OpenAI Responses API
        'supports_temperature': False,
        'supports_reasoning': True,
        # Astra rejects 'minimal' outright and adds a 'max' rung above 'xhigh'.
        'reasoning_efforts': ['low', 'medium', 'high', 'xhigh', 'max'],
    },
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
        'supports_reasoning': True,
        'reasoning_efforts': ['minimal', 'low', 'medium', 'high', 'xhigh'],
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
        'supports_reasoning': True,
        'reasoning_efforts': ['minimal', 'low', 'medium', 'high', 'xhigh'],
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
        'supports_reasoning': True,
        'reasoning_efforts': ['minimal', 'low', 'medium', 'high', 'xhigh'],
    }
}

# Every reasoning effort level the platform knows, ordered faster → smarter.
# Applied to the OpenAI Responses API `reasoning.effort` parameter for
# reasoning-capable models. ('none' is intentionally excluded — it disables
# reasoning entirely rather than sitting on this speed/intelligence ladder.)
# Keep in step with the frontend's REASONING_EFFORTS.
#
# This is the union across models, NOT what any one model accepts: the ends of
# the ladder are model-specific — the 5.6 suite takes 'minimal' but not 'max',
# Astra the reverse. Ask get_model_reasoning_efforts(model_id) for a model's
# real ladder; resolve_reasoning_effort() clamps onto it.
REASONING_EFFORT_CHOICES = [
    ('minimal', 'Minimal'),
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('xhigh', 'Extra High'),
    ('max', 'Max'),
]
REASONING_EFFORT_IDS = [effort_id for effort_id, _ in REASONING_EFFORT_CHOICES]
DEFAULT_REASONING_EFFORT = _BUILDER_SETTINGS.get('DEFAULT_REASONING_EFFORT', 'medium')

# Provider Choices
PROVIDER_CHOICES = [
    ('openai', 'OpenAI'),
]

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

    Without this, the underlying model has no knowledge of Imagi's model
    branding and will guess at its own identity when asked (often naming an
    older model like GPT-4o), which reads as if the wrong model is being used.

    Args:
        model_id: The public model ID (e.g. 'gpt-5.6-sol', 'gpt-6-astra')

    Returns:
        str: An instruction block to append to the agent's system prompt
    """
    display_name = get_model_display_name(model_id)
    return (
        "Model Identity:\n"
        f"- You are running as {display_name}, one of the models Imagi offers.\n"
        f"- If the user asks which model you are, answer '{display_name}'. Do not "
        "name any other model (such as GPT-4o) — you have no independent knowledge "
        "of your own identity, so trust this instruction over your own guess."
    )

def get_backend_model_id(model_id: str) -> str:
    """
    Resolve a public model id (e.g. 'gpt-5.6-sol') to the real underlying
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

def compute_cost_usd(model_id: str, input_tokens: int, output_tokens: int):
    """
    Compute the USD cost of a run from a suite model's per-million-token pricing.

    Args:
        model_id: The public model ID (e.g. 'gpt-5.6-sol', 'gpt-6-astra')
        input_tokens: Input tokens consumed by the run
        output_tokens: Output tokens produced by the run

    Returns:
        float or None: The cost in USD, or None when the model (or its
        pricing) is unknown so callers can omit cost cleanly.
    """
    model = get_model_by_id(model_id)
    if not model:
        return None
    input_price = model.get('input_price_per_m_tokens')
    output_price = model.get('output_price_per_m_tokens')
    if input_price is None or output_price is None:
        return None
    cost = (
        (input_tokens or 0) * input_price
        + (output_tokens or 0) * output_price
    ) / 1_000_000
    return round(cost, 6)

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

def get_model_reasoning_efforts(model_id: str) -> List[str]:
    """
    The reasoning effort levels a given model actually accepts, ordered
    faster → smarter. Empty when the model is unknown or has no reasoning.

    Args:
        model_id: The public model ID

    Returns:
        list: The model's accepted effort ids
    """
    model = get_model_by_id(model_id)
    if not model or not model.get('supports_reasoning'):
        return []
    efforts = model.get('reasoning_efforts')
    if not efforts:
        return list(REASONING_EFFORT_IDS)
    # Keep the canonical faster → smarter ordering regardless of how the
    # model entry happens to list them.
    return [effort for effort in REASONING_EFFORT_IDS if effort in efforts]


def _nearest_supported_effort(effort: str, supported: List[str]) -> str:
    """
    Clamp an effort level onto a model's ladder, picking the closest rung.

    Ties go to the smarter rung, so a request for an effort a model doesn't
    have never quietly buys *less* thinking than the neighbouring option.
    """
    if effort in supported:
        return effort
    order = REASONING_EFFORT_IDS
    target = order.index(effort) if effort in order else order.index(DEFAULT_REASONING_EFFORT)
    return min(
        supported,
        key=lambda candidate: (
            abs(order.index(candidate) - target),
            order.index(candidate) < target,
        ),
    )


def resolve_reasoning_effort(model_id: str, effort: str) -> str:
    """
    Resolve the reasoning effort to apply for a request.

    Returns None when the model does not support reasoning (so callers can omit
    the parameter entirely). Otherwise returns the requested effort, clamped
    onto the levels this model accepts — the ladder differs per model, and
    sending a level a model rejects (e.g. 'minimal' to Astra) fails the whole
    request. An unset or unrecognized effort falls back to the default, itself
    clamped the same way.

    Args:
        model_id: The public model ID
        effort: The requested reasoning effort level (may be None/invalid)

    Returns:
        str or None: An effort level this model accepts, or None if reasoning
        is unsupported
    """
    supported = get_model_reasoning_efforts(model_id)
    if not supported:
        return None
    if effort and is_valid_reasoning_effort(effort):
        return _nearest_supported_effort(effort, supported)
    return _nearest_supported_effort(DEFAULT_REASONING_EFFORT, supported)


 