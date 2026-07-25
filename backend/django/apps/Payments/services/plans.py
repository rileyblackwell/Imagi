"""
Subscription plan definitions for usage metering.

The single registry of plans and their rolling-window usage allowances. Plans
are code-defined (like Build's models_service.MODELS) so allowances ship with
the code; the database only stores which plan a user is on (models.Subscription).

Allowances are denominated in **US dollars of metered model spend**, not in
tokens. A run consumes its computed cost (see Build's models_service.
compute_cost_usd), so a pricier model or a heavier reasoning effort — which
produces more billed reasoning tokens — draws down the allowance faster. That
is the whole point of metering by cost: one allowance covers every model
instead of each needing its own token budget.

The allowance is *metered* spend, not a wallet: nothing is charged per run and
the numbers are approximate by design.

A plan is defined by its **weekly** allowance, and only the two rolling windows
below are tracked or shown. There is deliberately no monthly figure here: no
window enforces one, so carrying it would mean publishing a number the meter
never checks. What a plan costs per month is a Stripe price, not a limit.
"""

DEFAULT_PLAN_ID = 'free'

# The 5-hour burst window is a fifth of the weekly allowance: a single sitting
# can't drain the whole week, but five heavy sessions fill it. It exists to
# smooth load, not to be a second budget.
SESSIONS_PER_WEEK = 5


def _windows(weekly_usd):
    """The rolling-window allowances derived from a plan's weekly figure."""
    return {
        'weekly_usd': round(weekly_usd, 2),
        'five_hour_usd': round(weekly_usd / SESSIONS_PER_WEEK, 2),
    }


# Ids/names mirror the purchasable tiers on the pricing page (Free, Pro, Max).
# Pro's $10/week is the reference point: Free is a small taste of it, and the
# two Max tiers are literal 5x and 20x multiples of it (which is what "5x" and
# "20x" name). Max 20x allows more retail usage than its sticker price —
# viable because our per-token prices are marked up over real API cost.
PLANS = {
    'free': {
        'id': 'free',
        'name': 'Free',
        **_windows(2.5),
    },
    'pro': {
        'id': 'pro',
        'name': 'Pro',
        **_windows(10),
    },
    # Max is sold at two usage points (mirroring Claude's Max tier). They are
    # distinct plans, not one collapsed tier, so a 20x subscriber actually gets
    # 20x the allowance they pay for.
    'max_5x': {
        'id': 'max_5x',
        'name': 'Max (5x)',
        **_windows(50),
    },
    'max_20x': {
        'id': 'max_20x',
        'name': 'Max (20x)',
        **_windows(200),
    },
}

# Stripe price lookup_key -> registry plan id. The frontend pricing page
# (PricingView.vue) checks out by these lookup_keys, and the subscription
# webhook resolves them back to a plan through this map. The two Max price
# points map to their own tiers so 5x and 20x don't collapse to one allowance.
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
    """All plans (id, name, allowances) for the frontend's plan picker."""
    return list(PLANS.values())
