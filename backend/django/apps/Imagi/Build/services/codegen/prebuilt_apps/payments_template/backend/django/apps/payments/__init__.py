"""
Payments for this app's backend, maintained by Imagi.

    from apps.payments import has_active_plan, report_usage

    if not has_active_plan(request.user.email):
        ...  # send them to /pricing

    report_usage(request.user.email, quantity=1)  # pay-as-you-go plans

See client.py. Prices, customers and payments are managed in the Sell
console in Imagi.
"""
from .client import (  # noqa: F401
    PaymentsError,
    active_plans,
    has_active_plan,
    report_usage,
)
