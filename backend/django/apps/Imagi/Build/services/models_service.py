"""
Service for AI model operations in the Builder app.

This module provides centralized definitions for all AI models used across the application,
ensuring that model information (IDs, names, costs, etc.) is maintained in a single location.
"""

from typing import List, Optional, Tuple

from django.conf import settings

# Platform defaults for every user's project (see IMAGI_BUILDER in imagi/settings.py)
_BUILDER_SETTINGS = getattr(settings, 'IMAGI_BUILDER', {})

# Centralized Model Definitions
# The build workspace offers two families, each ordered faster → smarter.
# Anthropic's Claude:
#   Haiku 5.5   - fast and inexpensive, capable at most everyday edits
#   Sonnet 5.5  - quick and strong at everyday coding
#   Opus 5.5    - thoughtful all-rounder (default)
#   Fable 5.1   - Anthropic's most capable model, for the hardest work
# OpenAI's GPT (Riley, 2026-10-12, mainly for their faster service tiers):
#   GPT 6 Luna   - fast and inexpensive
#   GPT 6.1 Terra - quick and capable at half Sol's price (Riley, 2026-10-26)
#   GPT 6.1 Sol  - near-Astra intelligence at a fifth of the price
#   GPT 6 Astra  - OpenAI's most capable model
#
# `backend_model` is the real provider model id a public id maps to at
# runtime; for every current model the two coincide. Every model runs through
# the Agents SDK: Claude on the Anthropic Messages API
# (services/anthropic_model.py), GPT on the OpenAI Responses API.
#
# Prices are the provider's list price per million tokens, with no markup:
# a run draws down a user's allowance by what it actually costs (see
# Payments' plans.py). Cached input is billed at the provider's cached rate,
# since an agent loop resends most of its prompt every turn and the provider
# charges a small fraction for it. Haiku 5.5 publishes no separate cache-read
# rate, so its cached input is metered at the full input rate (never under).
# A model with `long_context_*` prices bills a request whose prompt is over
# `long_context_threshold_tokens` at those rates instead. Not modelled:
# Anthropic's 1.25x premium on writing the cache (those tokens bill at the
# plain input rate).
#
# `service_tiers` lists the faster OpenAI processing tiers a model offers
# (the request's service_tier), each with the multiplier it puts on every
# price line: Fast is twice the standard price, Ultrafast six times. A run
# with no tier is Standard.
#
# Every model climbs the same effort ladder — see REASONING_EFFORT_CHOICES
# below — up to its `max_reasoning_effort` (OpenAI's stops at xhigh).
MODELS = {
    'claude-haiku-5-5': {
        'id': 'claude-haiku-5-5',
        'name': 'Claude Haiku 5.5',
        'provider': 'anthropic',
        'type': 'anthropic',
        'backend_model': 'claude-haiku-5-5',
        'description': 'Anthropic | Claude Haiku 5.5 — fast and inexpensive, capable at most everyday edits',
        'capabilities': ['code_generation', 'chat', 'analysis'],
        'maxTokens': 1000000,
        'input_price_per_m_tokens': 0.1,
        'cached_input_price_per_m_tokens': 0.1,
        'output_price_per_m_tokens': 0.5,
        'long_context_threshold_tokens': 100_000,
        'long_context_input_price_per_m_tokens': 0.5,
        'long_context_cached_input_price_per_m_tokens': 0.5,
        'long_context_output_price_per_m_tokens': 2.5,
        'api_version': 'messages',
        'supports_temperature': False,
        'supports_reasoning': True,
        # Haiku has no server-side refusal fallback.
        'refusal_fallback': False,
    },
    'claude-sonnet-5-5': {
        'id': 'claude-sonnet-5-5',
        'name': 'Claude Sonnet 5.5',
        'provider': 'anthropic',
        'type': 'anthropic',
        'backend_model': 'claude-sonnet-5-5',
        'description': 'Anthropic | Claude Sonnet 5.5 — quick and strong at everyday coding',
        'capabilities': ['code_generation', 'chat', 'analysis'],
        'maxTokens': 1000000,
        'input_price_per_m_tokens': 2,
        'cached_input_price_per_m_tokens': 0.2,
        'output_price_per_m_tokens': 10,
        'api_version': 'messages',
        'supports_temperature': False,
        'supports_reasoning': True,
        'refusal_fallback': True,
    },
    'claude-opus-5-5': {
        'id': 'claude-opus-5-5',
        'name': 'Claude Opus 5.5',
        'provider': 'anthropic',
        'type': 'anthropic',
        'backend_model': 'claude-opus-5-5',
        'description': 'Anthropic | Claude Opus 5.5 — thoughtful and dependable, with strong judgment on code and design',
        'capabilities': ['code_generation', 'chat', 'analysis'],
        'maxTokens': 1000000,
        'input_price_per_m_tokens': 4,
        'cached_input_price_per_m_tokens': 0.2,
        'output_price_per_m_tokens': 20,
        'api_version': 'messages',
        'supports_temperature': False,
        'supports_reasoning': True,
        # Safety classifiers can decline a request; re-run it server-side on
        # Anthropic's recommended fallback instead of failing the turn.
        'refusal_fallback': True,
    },
    'claude-fable-5-1': {
        'id': 'claude-fable-5-1',
        'name': 'Claude Fable 5.1',
        'provider': 'anthropic',
        'type': 'anthropic',
        'backend_model': 'claude-fable-5-1',
        'description': "Anthropic | Claude Fable 5.1 — Anthropic's most capable model, for the hardest work",
        'capabilities': ['code_generation', 'chat', 'analysis'],
        'maxTokens': 1000000,
        'input_price_per_m_tokens': 10,
        'cached_input_price_per_m_tokens': 0.25,
        'output_price_per_m_tokens': 50,
        'api_version': 'messages',
        'supports_temperature': False,
        'supports_reasoning': True,
        'refusal_fallback': True,
    },
}

# OpenAI's long-context pricing: a request whose prompt is over 272K tokens
# bills input (cached too) at twice the short-context rate and output at one
# and a half times, the pattern OpenAI's GPT 6 price table follows.
OPENAI_LONG_CONTEXT_THRESHOLD = 272_000


def _openai_model(model_id, name, description, input_price, cached_price, output_price, service_tiers):
    return {
        'id': model_id,
        'name': name,
        'provider': 'openai',
        'type': 'openai',
        'backend_model': model_id,
        'description': description,
        'capabilities': ['code_generation', 'chat', 'analysis'],
        'input_price_per_m_tokens': input_price,
        'cached_input_price_per_m_tokens': cached_price,
        'output_price_per_m_tokens': output_price,
        'long_context_threshold_tokens': OPENAI_LONG_CONTEXT_THRESHOLD,
        'long_context_input_price_per_m_tokens': input_price * 2,
        'long_context_cached_input_price_per_m_tokens': cached_price * 2,
        'long_context_output_price_per_m_tokens': output_price * 1.5,
        'api_version': 'responses',
        'supports_reasoning': True,
        'max_reasoning_effort': 'xhigh',
        'service_tiers': service_tiers,
    }


MODELS.update({
    'gpt-6-luna': _openai_model(
        'gpt-6-luna', 'GPT 6 Luna',
        'OpenAI | GPT 6 Luna — fast and inexpensive, capable at most everyday edits',
        0.1, 0.01, 0.5, {'fast': 2},
    ),
    'gpt-6.1-terra': _openai_model(
        'gpt-6.1-terra', 'GPT 6.1 Terra',
        "OpenAI | GPT 6.1 Terra — quick and capable at half Sol's price",
        1, 0.05, 5, {'fast': 2},
    ),
    'gpt-6.1-sol': _openai_model(
        'gpt-6.1-sol', 'GPT 6.1 Sol',
        'OpenAI | GPT 6.1 Sol — near-Astra intelligence at a fraction of the price',
        2, 0.2, 10, {'fast': 2, 'ultrafast': 6},
    ),
    'gpt-6-astra': _openai_model(
        'gpt-6-astra', 'GPT 6 Astra',
        "OpenAI | GPT 6 Astra — OpenAI's most capable model, for the hardest work",
        10, 1, 50, {'fast': 2, 'ultrafast': 6},
    ),
})

# Models the platform used to offer, re-seated onto the current model for
# their tier. Conversations, dispatched threads and open client tabs can still
# carry these ids. They were re-seated onto Claude while the workspace ran on
# Anthropic only, and stay there so a conversation doesn't change provider.
LEGACY_MODEL_ALIASES = {
    'gpt-5.6-luna': 'claude-haiku-5-5',
    'gpt-5.6-terra': 'claude-opus-5-5',
    'gpt-5.6-sol': 'claude-opus-5-5',
}

# OpenAI's processing tiers, faster → pricier. '' is Standard, the default.
SERVICE_TIER_CHOICES = [
    ('', 'Standard'),
    ('fast', 'Fast'),
    ('ultrafast', 'Ultrafast'),
]
SERVICE_TIER_IDS = [tier for tier, _ in SERVICE_TIER_CHOICES if tier]

# The effort ladder, ordered faster → smarter: Claude's output_config.effort
# levels, the same for every model. Keep in step with the frontend's
# REASONING_EFFORTS.
REASONING_EFFORT_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('xhigh', 'Extra High'),
    ('max', 'Max'),
]
REASONING_EFFORT_IDS = [effort_id for effort_id, _ in REASONING_EFFORT_CHOICES]
DEFAULT_REASONING_EFFORT = _BUILDER_SETTINGS.get('DEFAULT_REASONING_EFFORT', 'medium')

# Rungs the platform used to offer, re-seated onto the ladder so a request from
# an older client tab still lands on the nearest real level instead of falling
# back to the default.
LEGACY_REASONING_EFFORT_ALIASES = {
    'minimal': 'low',
    'none': 'low',
}

# Provider Choices
PROVIDER_CHOICES = [
    ('openai', 'OpenAI'),
    ('anthropic', 'Anthropic'),
]

def get_model_choices() -> List[Tuple[str, str]]:
    """
    Get model choices for Django model fields.
    
    Returns:
        list: List of tuples with (id, name) for Django model choices
    """
    choices = [(model_id, model_data['name']) for model_id, model_data in MODELS.items()]
    # Retired ids stay valid choices: existing conversations still store them.
    choices += [
        (legacy_id, f"{legacy_id} (now {MODELS[successor]['name']})")
        for legacy_id, successor in LEGACY_MODEL_ALIASES.items()
    ]
    return choices

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

def canonical_model_id(model_id: str) -> str:
    """The current id for a model: a retired id maps to its successor."""
    return LEGACY_MODEL_ALIASES.get(model_id, model_id)

# A pricing id for a request made on a faster service tier:
# '<model id>:<tier>'. Only cost accounting sees it; the conversation still
# records the public model id.
TIER_PRICING_SEPARATOR = ':'


def supports_service_tier(model_id: str, tier: Optional[str]) -> bool:
    """Whether a model can be served on a faster tier ('fast', 'ultrafast')."""
    return bool(tier) and tier in ((get_model_by_id(model_id) or {}).get('service_tiers') or {})


def resolve_service_tier(model_id: str, tier: Optional[str]) -> Optional[str]:
    """The tier a run on this model asks for: the requested one when the
    model offers it, otherwise None (Standard)."""
    return tier if supports_service_tier(model_id, tier) else None


def split_pricing_id(pricing_id: str) -> Tuple[str, Optional[str]]:
    """A pricing id's model id and tier (None for Standard)."""
    if pricing_id and TIER_PRICING_SEPARATOR in pricing_id:
        model_id, tier = pricing_id.split(TIER_PRICING_SEPARATOR, 1)
        return model_id, tier
    return pricing_id, None


def pricing_model_id(model_id: str, tier: Optional[str] = None) -> str:
    """The id compute_cost_usd prices a run under: the model's own, or its
    tier's pricing id when the run asked for a tier the model has."""
    if supports_service_tier(model_id, tier):
        return f"{model_id}{TIER_PRICING_SEPARATOR}{tier}"
    return model_id


def get_model_by_id(model_id: str) -> dict:
    """
    Get a model definition by its ID. A retired id resolves to its
    successor's definition (see LEGACY_MODEL_ALIASES).
    
    Args:
        model_id: The model ID to look up
        
    Returns:
        dict: The model definition or None if not found
    """
    return MODELS.get(canonical_model_id(model_id))

def get_model_provider(model_id: str) -> str:
    """
    The provider that serves a model. Unknown ids report 'anthropic', the
    default model's provider.
    """
    model = get_model_by_id(model_id)
    return model.get('provider', 'anthropic') if model else 'anthropic'

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

def get_backend_model_id(model_id: str) -> str:
    """
    Resolve a public model id (e.g. 'claude-opus-5-5', or a retired 'gpt-6-luna')
    to the real underlying provider model id used for API calls.

    Falls back to the given id when the model is unknown or defines no explicit
    backend model, so callers always receive a usable string.

    Args:
        model_id: The public model ID

    Returns:
        str: The underlying provider model id to send to the API
    """
    model = get_model_by_id(model_id)
    if model and model.get('backend_model'):
        return model['backend_model']
    return model_id

def long_context_threshold(model_id: str):
    """The prompt size above which a model (or a pricing id) bills at its
    long-context rates, or None when it has no such tier."""
    model = get_model_by_id(split_pricing_id(model_id)[0])
    return (model or {}).get('long_context_threshold_tokens')


def compute_cost_usd(
    model_id: str,
    input_tokens: int,
    output_tokens: int,
    cached_input_tokens: int = 0,
    long_context_input_tokens: int = 0,
    long_context_cached_tokens: int = 0,
    long_context_output_tokens: int = 0,
):
    """
    Compute the USD cost of a run at the model's list price.

    Args:
        model_id: The public model ID (e.g. 'claude-opus-5-5'), or a tier
            pricing id from pricing_model_id ('gpt-6.1-sol:ultrafast')
        input_tokens: All input tokens the run consumed, cached ones included
        output_tokens: Output tokens produced by the run
        cached_input_tokens: How many of input_tokens were served from the
            provider's prompt cache; they bill at the cached-input rate
        long_context_*: The share of each count that came from requests over
            the model's long-context threshold (see base_agent.long_context_tokens);
            billed at the long-context rates when the model has them

    Returns:
        float or None: The cost in USD, or None when the model (or its
        pricing) is unknown so callers can omit cost cleanly.
    """
    model_id, tier = split_pricing_id(model_id)
    model = get_model_by_id(model_id)
    if not model:
        return None
    multiplier = (model.get('service_tiers') or {}).get(tier, 1)
    input_price = model.get('input_price_per_m_tokens')
    output_price = model.get('output_price_per_m_tokens')
    if input_price is None or output_price is None:
        return None
    cached_price = model.get('cached_input_price_per_m_tokens', input_price)

    def clamp(value, ceiling):
        return min(max(value or 0, 0), ceiling or 0)

    # A part can't exceed the whole it is part of.
    input_tokens = input_tokens or 0
    output_tokens = output_tokens or 0
    cached = clamp(cached_input_tokens, input_tokens)
    long_in = long_cached = long_out = 0
    if model.get('long_context_threshold_tokens'):
        long_in = clamp(long_context_input_tokens, input_tokens)
        long_cached = clamp(long_context_cached_tokens, min(long_in, cached))
        long_out = clamp(long_context_output_tokens, output_tokens)

    cost = (
        ((input_tokens - long_in) - (cached - long_cached)) * input_price
        + (cached - long_cached) * cached_price
        + (output_tokens - long_out) * output_price
    )
    if long_in or long_out:
        cost += (
            (long_in - long_cached) * model['long_context_input_price_per_m_tokens']
            + long_cached * model.get(
                'long_context_cached_input_price_per_m_tokens',
                model['long_context_input_price_per_m_tokens'],
            )
            + long_out * model['long_context_output_price_per_m_tokens']
        )
    return round(cost * multiplier / 1_000_000, 6)

def is_valid_reasoning_effort(effort: str) -> bool:
    """Whether the given reasoning effort level is on the platform ladder."""
    return effort in REASONING_EFFORT_IDS

def canonical_reasoning_effort(effort: Optional[str]) -> Optional[str]:
    """An effort on the ladder: itself, a legacy rung's successor, or None
    when it is neither (for callers that refuse rather than fall back)."""
    if effort and is_valid_reasoning_effort(effort):
        return effort
    return LEGACY_REASONING_EFFORT_ALIASES.get(effort or '')

def model_supports_reasoning(model_id: str) -> bool:
    """
    Whether the model supports the reasoning 'effort' parameter.
    Defaults to False when the model is unknown.
    """
    model = get_model_by_id(model_id)
    if not model:
        return False
    return model.get('supports_reasoning', False)

def _cap_effort(model_id: str, effort: str) -> str:
    """An effort no higher than the model's top rung ('max' is Claude's
    alone; OpenAI's ladder stops at xhigh)."""
    top = (get_model_by_id(model_id) or {}).get('max_reasoning_effort')
    if top and REASONING_EFFORT_IDS.index(effort) > REASONING_EFFORT_IDS.index(top):
        return top
    return effort

def resolve_reasoning_effort(model_id: str, effort: str) -> str:
    """
    Resolve the reasoning effort to apply for a request.

    Returns None when the model does not support reasoning (so callers can omit
    the parameter entirely). Otherwise returns the requested effort when it is
    on the ladder; a legacy rung ('minimal') is re-seated onto its
    nearest real level, and anything else — unset, empty, or unrecognized —
    falls back to the default. The result is always a value the SDK accepts,
    so reasoning is applied rather than dropped.

    Args:
        model_id: The public model ID
        effort: The requested reasoning effort level (may be None/invalid)

    Returns:
        str or None: An effort level on the ladder, or None if reasoning is
        unsupported
    """
    if not model_supports_reasoning(model_id):
        return None
    if not (effort and is_valid_reasoning_effort(effort)):
        effort = LEGACY_REASONING_EFFORT_ALIASES.get(effort, DEFAULT_REASONING_EFFORT)
    return _cap_effort(model_id, effort)
