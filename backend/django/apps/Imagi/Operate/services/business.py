"""
The business half of the Operate dashboard: revenue, expenses and profit.

Revenue has two sources: payments taken through Sell (paid orders) and any
other income recorded in the ledger (including invoices marked paid). Expenses
come from the ledger only. Profit is revenue minus expenses. Sell's numbers
are read through `sell_revenue_by_month` alone, so when Sell moves to the
user's own Stripe account only that function has to follow it.
"""

import datetime

from django.db.models import Q, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone

from apps.Imagi.Sell.models import Order, SellSettings

from ..models import Transaction

WINDOW_DAYS = 30
MONTHS = 6


def money(value) -> float:
    """Aggregate sums come back as Decimal or None; emit a plain number."""
    return float(value or 0)


def months_back(today: datetime.date, months: int) -> datetime.date:
    """First day of the month `months - 1` months before today's."""
    year, month = today.year, today.month
    for _ in range(months - 1):
        month -= 1
        if month == 0:
            year, month = year - 1, 12
    return datetime.date(year, month, 1)


def sell_revenue_since(project, since) -> float:
    cents = project.sell_orders.filter(
        status__in=Order.PAID_STATUSES, paid_at__gte=since
    ).aggregate(total=Sum('amount_total_cents'))['total']
    return round((cents or 0) / 100.0, 2)


def sell_revenue_by_month(project, start: datetime.date) -> dict:
    rows = (
        project.sell_orders
        .filter(status__in=Order.PAID_STATUSES, paid_at__date__gte=start)
        .annotate(month=TruncMonth('paid_at'))
        .values('month')
        .annotate(total=Sum('amount_total_cents'))
    )
    return {row['month'].strftime('%Y-%m'): (row['total'] or 0) / 100.0 for row in rows}


def business_summary(project) -> dict:
    """Everything the dashboard's business half shows."""
    settings_obj = SellSettings.objects.filter(project=project).first()
    today = timezone.localdate()
    since_date = today - datetime.timedelta(days=WINDOW_DAYS)
    since = timezone.now() - datetime.timedelta(days=WINDOW_DAYS)

    ledger = project.operate_transactions.all()
    window = ledger.filter(occurred_on__gte=since_date).aggregate(
        income=Sum('amount', filter=Q(kind=Transaction.KIND_INCOME)),
        expenses=Sum('amount', filter=Q(kind=Transaction.KIND_EXPENSE)),
    )
    sell_30d = sell_revenue_since(project, since)
    recorded_30d = money(window['income'])
    revenue_30d = round(sell_30d + recorded_30d, 2)
    expenses_30d = money(window['expenses'])

    # Month by month: revenue (Sell + recorded income) against expenses.
    start = months_back(today, MONTHS)
    sell_by_month = sell_revenue_by_month(project, start)
    ledger_rows = (
        ledger.filter(occurred_on__gte=start)
        .annotate(month=TruncMonth('occurred_on'))
        .values('month', 'kind')
        .annotate(total=Sum('amount'))
    )
    by_month = {}
    for row in ledger_rows:
        bucket = by_month.setdefault(row['month'].strftime('%Y-%m'), {'income': 0.0, 'expenses': 0.0})
        key = 'income' if row['kind'] == Transaction.KIND_INCOME else 'expenses'
        bucket[key] = money(row['total'])

    series = []
    cursor = start
    while cursor <= today:
        key = cursor.strftime('%Y-%m')
        bucket = by_month.get(key, {'income': 0.0, 'expenses': 0.0})
        revenue = round(bucket['income'] + sell_by_month.get(key, 0.0), 2)
        series.append({
            'month': key,
            'label': cursor.strftime('%b'),
            'income': revenue,
            'expenses': bucket['expenses'],
            'net': round(revenue - bucket['expenses'], 2),
        })
        cursor = (cursor + datetime.timedelta(days=32)).replace(day=1)

    return {
        'currency': settings_obj.currency if settings_obj else 'usd',
        'sell_connected': bool(settings_obj and settings_obj.is_configured),
        'has_ledger': ledger.exists(),
        'revenue_30d': revenue_30d,
        'revenue_sell_30d': sell_30d,
        'revenue_recorded_30d': recorded_30d,
        'expenses_30d': expenses_30d,
        'profit_30d': round(revenue_30d - expenses_30d, 2),
        'monthly': series,
    }
