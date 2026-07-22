"""
Subscription plan definitions for usage-limit metering.

The single registry of plans and their rolling-window token limits. Plans are
code-defined (like Build's models_service.MODELS) so limits ship with the
code; the database only stores which plan a user is on (models.Subscription).
"""

DEFAULT_PLAN_ID = 'starter'

PLANS = {
    'starter': {
        'id': 'starter',
        'name': 'Starter',
        'five_hour_tokens': 2_000_000,
        'weekly_tokens': 20_000_000,
    },
    'pro': {
        'id': 'pro',
        'name': 'Pro',
        'five_hour_tokens': 10_000_000,
        'weekly_tokens': 100_000_000,
    },
    'scale': {
        'id': 'scale',
        'name': 'Scale',
        'five_hour_tokens': 30_000_000,
        'weekly_tokens': 300_000_000,
    },
}


def get_plan(plan_id):
    """Return the plan definition for an id, falling back to the default plan.

    Unknown ids resolve to 'starter' so a stale/renamed plan value in the
    database can never disable metering.
    """
    plan = PLANS.get(plan_id)
    return plan if plan else PLANS[DEFAULT_PLAN_ID]


def get_plan_for_user(user):
    """Return the plan definition for a user (no Subscription row -> starter)."""
    from ..models import Subscription

    subscription = Subscription.objects.filter(user=user).first()
    return get_plan(subscription.plan if subscription else DEFAULT_PLAN_ID)


def list_plans():
    """All plans (id, name, limits) for the frontend's plan picker."""
    return list(PLANS.values())
