"""
The plan registry for usage metering.

Imagi has one plan, Free, and nothing is sold. The paid plans (Pro and the two
Max tiers) and their Stripe subscription flow were removed; if paid plans come
back, they are added here as new entries alongside Free, with the checkout and
webhook that grant them.

Plans are code-defined (like Build's models_service.MODELS) so the allowance
ships with the code. The database's Subscription row stores which plan a user
is on, and a user with no row is on Free; any stored id that is not a plan here
also resolves to Free, so a leftover value can never disable metering.

The allowance is denominated in **US dollars of metered model spend**, not in
tokens. A run consumes its computed cost (see Build's models_service.
compute_cost_usd), so a pricier model or a heavier reasoning effort — which
produces more billed reasoning tokens — draws down the allowance faster. One
allowance covers every model, Anthropic and OpenAI alike.

The allowance is *metered* spend, not a wallet: nothing is charged per run and
the numbers are approximate by design.

The plan is defined by a single **weekly** allowance over a rolling 7 days, and
that one window is all that is tracked, enforced, or shown. There was once a
second, 5-hour burst window; it was removed, and the weekly allowance alone is
what bounds spend. Every plan must have one: there is no unlimited plan.
"""

DEFAULT_PLAN_ID = 'free'

# How many active projects a plan may hold at once; None means no limit.
# Enforced when a project is created (ProjectCreateView). Free has none: its
# weekly allowance is its only limit.
UNLIMITED_PROJECTS = None

PLANS = {
    # $20 a week of combined Anthropic and OpenAI spend at list price.
    'free': {
        'id': 'free',
        'name': 'Free',
        'weekly_usd': 20.0,
        'max_active_projects': UNLIMITED_PROJECTS,
    },
}


def get_plan(plan_id):
    """Return the plan definition for an id, falling back to the default plan.

    Unknown ids (including the retired pro/max ids) resolve to 'free' so a
    stale plan value in the database can never disable metering.
    """
    return PLANS.get(plan_id) or PLANS[DEFAULT_PLAN_ID]


def get_plan_for_user(user):
    """Return the plan definition for a user (no Subscription row -> free)."""
    from ..models import Subscription

    subscription = Subscription.objects.filter(user=user).first()
    return get_plan(subscription.plan if subscription else DEFAULT_PLAN_ID)


def check_project_limit(user):
    """Whether the user's plan lets them create another project.

    Returns (allowed, payload): payload is None when allowed, and otherwise
    the error body the create endpoint returns, naming the plan and its limit
    so the message can say what to do about it.
    """
    from apps.Imagi.ProjectManager.models import Project

    plan = get_plan_for_user(user)
    limit = plan.get('max_active_projects')
    if limit is None:
        return True, None
    active = Project.objects.filter(user=user, is_active=True).count()
    if active < limit:
        return True, None
    included = 'one project' if limit == 1 else f'{limit} projects'
    return False, {
        'error': (
            f"The {plan['name']} plan includes {included}. Delete a project "
            "to make room for a new one."
        ),
        'code': 'project_limit',
        'plan': {'id': plan['id'], 'name': plan['name']},
        'max_active_projects': limit,
        'active_projects': active,
    }


def list_plans():
    """All plans (id, name, allowance) for the frontend."""
    return list(PLANS.values())
