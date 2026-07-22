"""
Token-usage metering and rolling-window plan limits.

Records one UsageEvent per agent run whose usage was captured, and computes
5-hour / weekly rolling windows against the user's plan limits. The Build app
enforces limits at its run entrypoints and records usage after each run; this
module owns the arithmetic.
"""

import logging
from datetime import timedelta

from django.db.models import Min, Sum
from django.utils import timezone

from ..models import UsageEvent
from .plans import get_plan_for_user

logger = logging.getLogger(__name__)

FIVE_HOUR_WINDOW = timedelta(hours=5)
WEEKLY_WINDOW = timedelta(days=7)


def record_usage(user, model_name, input_tokens, output_tokens, conversation_id=None):
    """Record one run's token usage as an append-only UsageEvent.

    Skips silently when both token counts are falsy: absent usage means the
    run's tokens were never captured (unknown), and recording a zero-token
    event would misreport it as free.
    """
    if not input_tokens and not output_tokens:
        return None
    input_tokens = int(input_tokens or 0)
    output_tokens = int(output_tokens or 0)
    return UsageEvent.objects.create(
        user=user,
        model_name=model_name,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=input_tokens + output_tokens,
        conversation_id=conversation_id,
    )


def _window_status(user, window, limit, now):
    """Usage within a rolling window: {'used', 'limit', 'resets_at'}.

    resets_at is when the oldest counted event ages out of the window — the
    earliest moment 'used' can decrease — and None while nothing is counted.
    """
    aggregate = UsageEvent.objects.filter(
        user=user, created_at__gte=now - window
    ).aggregate(used=Sum('total_tokens'), oldest=Min('created_at'))
    used = aggregate['used'] or 0
    resets_at = (aggregate['oldest'] + window) if used else None
    return {
        'used': used,
        'limit': limit,
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
                user, FIVE_HOUR_WINDOW, plan['five_hour_tokens'], now
            ),
            'weekly': _window_status(
                user, WEEKLY_WINDOW, plan['weekly_tokens'], now
            ),
        },
    }


def check_usage_allowed(user):
    """Whether the user may start an agent run: (allowed, payload).

    When allowed, the payload is the full usage status. When refused, the
    payload identifies the exceeded window and is shaped for a pre-stream
    429 response body: {'error', 'detail', 'window', 'resets_at'}.
    """
    status = get_usage_status(user)
    plan_name = status['plan']['name']
    for window_key, window_name, label in (
        ('5h', 'five_hour', '5-hour'),
        ('week', 'weekly', 'weekly'),
    ):
        window = status['windows'][window_name]
        if window['used'] >= window['limit']:
            return False, {
                'error': 'usage_limit_exceeded',
                'detail': (
                    f"You've reached the {label} usage limit of the {plan_name} "
                    "plan. Usage frees up as older activity ages out of the "
                    "window — or upgrade your plan for a higher limit."
                ),
                'window': window_key,
                'resets_at': window['resets_at'],
            }
    return True, status
