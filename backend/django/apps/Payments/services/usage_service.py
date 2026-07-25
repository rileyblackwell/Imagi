"""
Cost-based usage metering and rolling-window plan allowances.

Records one UsageEvent per agent run whose usage was captured, and computes
5-hour / weekly rolling windows against the user's plan allowance. The Build
app enforces allowances at its run entrypoints and records usage after each
run; this module owns the arithmetic.

Everything here is denominated in US dollars of metered model spend. Tokens are
still stored per event for reporting, but they are never what a window is
measured against — a run's *cost* is, so choosing a pricier model or a heavier
reasoning effort draws the allowance down faster.
"""

import logging
from datetime import timedelta
from decimal import Decimal

from django.db.models import Min, Sum
from django.utils import timezone

from ..models import UsageEvent
from .plans import get_plan_for_user

logger = logging.getLogger(__name__)

FIVE_HOUR_WINDOW = timedelta(hours=5)
WEEKLY_WINDOW = timedelta(days=7)

# Per-million-token prices used only when a run's cost could not be computed
# (an unpriced or unknown model). Deliberately the priciest tier in Build's
# models_service, so an unpriced model meters conservatively instead of
# metering as free — unknown must never be the cheap path.
FALLBACK_INPUT_PRICE_PER_M = Decimal('6')
FALLBACK_OUTPUT_PRICE_PER_M = Decimal('30')


def _fallback_cost(input_tokens, output_tokens):
    """Conservative cost for a run whose model pricing was unavailable."""
    return (
        Decimal(input_tokens) * FALLBACK_INPUT_PRICE_PER_M
        + Decimal(output_tokens) * FALLBACK_OUTPUT_PRICE_PER_M
    ) / Decimal('1000000')


def record_usage(
    user,
    model_name,
    input_tokens,
    output_tokens,
    cost_usd=None,
    conversation_id=None,
):
    """Record one run's usage as an append-only UsageEvent.

    Skips silently when both token counts are falsy: absent usage means the
    run's tokens were never captured (unknown), and recording a zero-token
    event would misreport it as free.

    cost_usd is the caller's computed cost for the run. When it is absent (the
    model had no pricing), the cost is estimated at the fallback rate rather
    than stored as zero — a run we couldn't price still consumed allowance.
    """
    if not input_tokens and not output_tokens:
        return None
    input_tokens = int(input_tokens or 0)
    output_tokens = int(output_tokens or 0)
    if cost_usd is None:
        cost = _fallback_cost(input_tokens, output_tokens)
    else:
        cost = Decimal(str(cost_usd))
    return UsageEvent.objects.create(
        user=user,
        model_name=model_name,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=input_tokens + output_tokens,
        cost_usd=cost,
        conversation_id=conversation_id,
    )


def _window_status(user, window, limit_usd, now):
    """Usage within a rolling window: {'used_usd', 'limit_usd', 'resets_at'}.

    resets_at is when the oldest counted event ages out of the window — the
    earliest moment 'used_usd' can decrease — and None while nothing is
    counted. The keys are explicitly dollar-suffixed so a client written
    against the old token-denominated payload reads them as absent (unknown)
    rather than silently rendering dollars as tokens.
    """
    aggregate = UsageEvent.objects.filter(
        user=user, created_at__gte=now - window
    ).aggregate(used=Sum('cost_usd'), oldest=Min('created_at'))
    used = float(aggregate['used'] or 0)
    # Anchor the reset on the oldest event only when something is counted; a
    # window summing to exactly $0.00 of priced usage still has events in it.
    resets_at = aggregate['oldest'] + window if aggregate['oldest'] else None
    return {
        'used_usd': round(used, 4),
        'limit_usd': limit_usd,
        'resets_at': resets_at.isoformat() if resets_at else None,
    }


def get_usage_status(user):
    """The user's plan and both rolling usage windows, for display."""
    plan = get_plan_for_user(user)
    now = timezone.now()
    return {
        'plan': {'id': plan['id'], 'name': plan['name']},
        'windows': {
            'five_hour': _window_status(
                user, FIVE_HOUR_WINDOW, plan['five_hour_usd'], now
            ),
            'weekly': _window_status(
                user, WEEKLY_WINDOW, plan['weekly_usd'], now
            ),
        },
    }


def check_usage_allowed(user):
    """Whether the user may start an agent run: (allowed, payload).

    When allowed, the payload is the full usage status. When refused, the
    payload identifies the exhausted window and is shaped for a pre-stream
    429 response body: {'error', 'detail', 'window', 'resets_at'}.
    """
    status = get_usage_status(user)
    plan_name = status['plan']['name']
    for window_key, window_name, label in (
        ('5h', 'five_hour', '5-hour'),
        ('week', 'weekly', 'weekly'),
    ):
        window = status['windows'][window_name]
        if window['used_usd'] >= window['limit_usd']:
            return False, {
                'error': 'usage_limit_exceeded',
                'detail': (
                    f"You've used the {label} usage allowance of the "
                    f"{plan_name} plan. Allowance frees up as older activity "
                    "ages out of the window — or upgrade your plan for more. "
                    "Choosing a lighter model or lower reasoning effort also "
                    "makes your allowance go further."
                ),
                'window': window_key,
                'resets_at': window['resets_at'],
            }
    return True, status
