"""
Bridge to the Payments app's usage metering.

The Payments app owns plan definitions, usage events, and window arithmetic
(apps.Payments.services.usage_service / plans); Build enforces limits at its
run entrypoints and records each run's tokens. This wrapper is the single
point of Build -> Payments coupling, imported lazily so Build stays loadable
without the Payments app (e.g. in isolated tests).
"""


def check_usage_allowed(user):
    """(allowed, payload) — see Payments' usage_service.check_usage_allowed."""
    from apps.Payments.services.usage_service import check_usage_allowed as check
    return check(user)


def record_usage(
    user,
    model_name,
    input_tokens,
    output_tokens,
    cost_usd=None,
    conversation_id=None,
):
    """Record a run's usage and metered cost — see usage_service.record_usage.

    cost_usd is what the run draws from the plan allowance; passing None means
    the run could not be priced, and Payments meters it conservatively rather
    than as free.
    """
    from apps.Payments.services.usage_service import record_usage as record
    return record(
        user,
        model_name,
        input_tokens,
        output_tokens,
        cost_usd=cost_usd,
        conversation_id=conversation_id,
    )
