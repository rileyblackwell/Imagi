"""
Subscription plan definitions for usage-limit metering.

The single registry of plans and their rolling-window token limits. Plans are
code-defined (like Build's models_service.MODELS) so limits ship with the
code; the database only stores which plan a user is on (models.Subscription).
"""

DEFAULT_PLAN_ID = 'free'

# Ids/names mirror the purchasable tiers on the pricing page (Free, Pro, Max).
PLANS = {
    'free': {
        'id': 'free',
        'name': 'Free',
        'five_hour_tokens': 2_000_000,
        'weekly_tokens': 20_000_000,
    },
    'pro': {
        'id': 'pro',
        'name': 'Pro',
        'five_hour_tokens': 10_000_000,
        'weekly_tokens': 100_000_000,
    },
    # Max is sold at two usage points (mirroring Claude's Max tier). They are
    # distinct plans, not one collapsed tier, so a 20x subscriber actually gets
    # 20x the limits they pay for. Limits are exact multiples of Pro.
    'max_5x': {
        'id': 'max_5x',
        'name': 'Max (5x)',
        'five_hour_tokens': 50_000_000,
        'weekly_tokens': 500_000_000,
    },
    'max_20x': {
        'id': 'max_20x',
        'name': 'Max (20x)',
        'five_hour_tokens': 200_000_000,
        'weekly_tokens': 2_000_000_000,
    },
}

# Stripe price lookup_key -> registry plan id. The frontend pricing page
# (PricingView.vue) checks out by these lookup_keys, and the subscription
# webhook resolves them back to a plan through this map. The two Max price
# points map to their own tiers so 5x and 20x don't collapse to one limit.
LOOKUP_KEY_TO_PLAN = {
    'pro_monthly': 'pro',
    'max_5x_monthly': 'max_5x',
    'max_20x_monthly': 'max_20x',
}


def plan_id_for_lookup_key(lookup_key):
    """Resolve a Stripe price lookup_key to a registry plan id, or None.

    Prefers the explicit lookup_key map; falls back to treating a lookup_key
    that is itself a plan id as that plan (so a price configured directly with
    a plan-id lookup_key still resolves).
    """
    if lookup_key in LOOKUP_KEY_TO_PLAN:
        return LOOKUP_KEY_TO_PLAN[lookup_key]
    if lookup_key in PLANS:
        return lookup_key
    return None


def get_plan(plan_id):
    """Return the plan definition for an id, falling back to the default plan.

    Unknown ids resolve to 'free' so a stale/renamed plan value in the
    database can never disable metering.
    """
    plan = PLANS.get(plan_id)
    return plan if plan else PLANS[DEFAULT_PLAN_ID]


def get_plan_for_user(user):
    """Return the plan definition for a user (no Subscription row -> free)."""
    from ..models import Subscription

    subscription = Subscription.objects.filter(user=user).first()
    return get_plan(subscription.plan if subscription else DEFAULT_PLAN_ID)


def list_plans():
    """All plans (id, name, limits) for the frontend's plan picker."""
    return list(PLANS.values())
