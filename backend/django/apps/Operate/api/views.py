"""
API views for the Operate app.

Everything is scoped to a project owned by the authenticated user:
/api/v1/operate/projects/<project_id>/...

The dashboard endpoint is the "central hub" view: it aggregates the
project's finances, invoices, and tasks, and pulls in a pulse from the
other workspace modules (marketing today; sales later) so the business
can be read at a glance from one place.
"""

import datetime

from django.db.models import Count, F, Q, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.Marketing.models import Campaign, Contact, MarketingSettings, Message
from apps.Products.Imagi.ProjectManager.models import Project
from apps.Sell.models import Order, SellSettings

from ..models import Invoice, OperationsTask, Transaction
from .serializers import (
    InvoiceSerializer,
    OperationsTaskSerializer,
    TransactionSerializer,
)

CASHFLOW_MONTHS = 6


def paginate(request, queryset, default_limit=50, max_limit=200):
    """Slice a queryset by ?limit=&offset= and return (page, total)."""
    try:
        limit = int(request.query_params.get('limit', default_limit))
    except (TypeError, ValueError):
        limit = default_limit
    limit = max(1, min(limit, max_limit))
    try:
        offset = max(int(request.query_params.get('offset', 0)), 0)
    except (TypeError, ValueError):
        offset = 0
    return queryset[offset:offset + limit], queryset.count()


def money(value) -> float:
    """Aggregate sums come back as Decimal or None; emit a plain number."""
    return float(value or 0)


class ProjectScopedView(APIView):
    """Base view resolving the project from the URL and enforcing ownership."""

    permission_classes = [IsAuthenticated]

    def get_project(self) -> Project:
        try:
            return Project.objects.get(
                id=self.kwargs['project_id'],
                user=self.request.user,
                is_active=True,
            )
        except Project.DoesNotExist:
            raise NotFound('Project not found')


# -- Dashboard -------------------------------------------------------------------


def cashflow_series(project, months=CASHFLOW_MONTHS):
    """Income/expense totals per calendar month for the last `months` months."""
    today = timezone.localdate()
    start = (today.replace(day=1) - datetime.timedelta(days=(months - 1) * 31)).replace(day=1)
    rows = (
        project.operate_transactions
        .filter(occurred_on__gte=start)
        .annotate(month=TruncMonth('occurred_on'))
        .values('month', 'kind')
        .annotate(total=Sum('amount'))
    )
    by_month = {}
    for row in rows:
        key = row['month'].strftime('%Y-%m')
        bucket = by_month.setdefault(key, {'income': 0.0, 'expenses': 0.0})
        if row['kind'] == Transaction.KIND_INCOME:
            bucket['income'] = money(row['total'])
        else:
            bucket['expenses'] = money(row['total'])

    series = []
    cursor = start
    while cursor <= today:
        key = cursor.strftime('%Y-%m')
        bucket = by_month.get(key, {'income': 0.0, 'expenses': 0.0})
        series.append({
            'month': key,
            'label': cursor.strftime('%b'),
            'income': bucket['income'],
            'expenses': bucket['expenses'],
            'net': round(bucket['income'] - bucket['expenses'], 2),
        })
        cursor = (cursor + datetime.timedelta(days=32)).replace(day=1)
    return series


def marketing_pulse(project) -> dict:
    """Snapshot of the Market module for the cross-module section."""
    settings_obj = MarketingSettings.objects.filter(project=project).first()
    since = timezone.now() - datetime.timedelta(days=30)
    messages = project.marketing_messages.all()
    return {
        'configured': bool(settings_obj and settings_obj.is_configured),
        'contacts_total': project.marketing_contacts.count(),
        'contacts_subscribed': project.marketing_contacts.filter(
            consent=Contact.CONSENT_SUBSCRIBED
        ).count(),
        'campaigns_active': project.marketing_campaigns.filter(
            status__in=[Campaign.STATUS_SCHEDULED, Campaign.STATUS_SENDING]
        ).count(),
        'messages_sent_30d': messages.filter(
            direction=Message.DIRECTION_OUTBOUND, created_at__gte=since
        ).count(),
        'replies_30d': messages.filter(
            direction=Message.DIRECTION_INBOUND, created_at__gte=since
        ).count(),
    }


def sell_pulse(project) -> dict:
    """Snapshot of the Sell module for the cross-module section."""
    settings_obj = SellSettings.objects.filter(project=project).first()
    since = timezone.now() - datetime.timedelta(days=30)
    orders = project.sell_orders.all()
    paid_30d = orders.filter(status__in=Order.PAID_STATUSES, paid_at__gte=since).aggregate(
        revenue_cents=Sum('amount_total_cents'), count=Count('id')
    )
    return {
        'configured': bool(settings_obj and settings_obj.is_configured),
        'currency': settings_obj.currency if settings_obj else 'usd',
        'products_active': project.sell_products.filter(is_active=True).count(),
        'customers_total': project.sell_customers.count(),
        'orders_pending': orders.filter(status=Order.STATUS_PENDING).count(),
        'orders_paid_30d': paid_30d['count'] or 0,
        'revenue_30d': round((paid_30d['revenue_cents'] or 0) / 100.0, 2),
    }


class DashboardView(ProjectScopedView):
    """Aggregated stats for the Operate hub."""

    def get(self, request, project_id):
        project = self.get_project()
        today = timezone.localdate()
        since_30d = today - datetime.timedelta(days=30)
        soon = today + datetime.timedelta(days=7)

        transactions = project.operate_transactions.all()
        window = transactions.filter(occurred_on__gte=since_30d)
        totals = window.aggregate(
            income=Sum('amount', filter=Q(kind=Transaction.KIND_INCOME)),
            expenses=Sum('amount', filter=Q(kind=Transaction.KIND_EXPENSE)),
        )
        all_time = transactions.aggregate(
            income=Sum('amount', filter=Q(kind=Transaction.KIND_INCOME)),
            expenses=Sum('amount', filter=Q(kind=Transaction.KIND_EXPENSE)),
        )

        invoices = project.operate_invoices.all()
        open_invoices = invoices.filter(status=Invoice.STATUS_SENT)
        invoice_stats = open_invoices.aggregate(
            outstanding=Sum('total'), count=Count('id')
        )
        overdue_count = open_invoices.filter(due_date__lt=today).count()
        paid_30d = invoices.filter(
            status=Invoice.STATUS_PAID, paid_at__date__gte=since_30d
        ).aggregate(total=Sum('total'))

        tasks = project.operate_tasks.all()
        open_tasks = tasks.exclude(status=OperationsTask.STATUS_DONE)

        income_30d = money(totals['income'])
        expenses_30d = money(totals['expenses'])
        return Response({
            'finance': {
                'income_30d': income_30d,
                'expenses_30d': expenses_30d,
                'net_30d': round(income_30d - expenses_30d, 2),
                'income_all_time': money(all_time['income']),
                'expenses_all_time': money(all_time['expenses']),
                'transactions_total': transactions.count(),
            },
            'cashflow': cashflow_series(project),
            'invoices': {
                'outstanding_total': money(invoice_stats['outstanding']),
                'outstanding_count': invoice_stats['count'] or 0,
                'overdue_count': overdue_count,
                'draft_count': invoices.filter(status=Invoice.STATUS_DRAFT).count(),
                'paid_30d': money(paid_30d['total']),
            },
            'tasks': {
                'open_count': open_tasks.count(),
                'in_progress_count': open_tasks.filter(
                    status=OperationsTask.STATUS_IN_PROGRESS
                ).count(),
                'overdue_count': open_tasks.filter(due_date__lt=today).count(),
                'due_soon_count': open_tasks.filter(
                    due_date__gte=today, due_date__lte=soon
                ).count(),
            },
            'marketing': marketing_pulse(project),
            'sell': sell_pulse(project),
            'recent_transactions': TransactionSerializer(
                transactions.select_related('invoice')[:5], many=True
            ).data,
            'open_invoices': InvoiceSerializer(
                open_invoices.order_by('due_date', '-created_at')[:5], many=True
            ).data,
            'upcoming_tasks': OperationsTaskSerializer(
                open_tasks.order_by(
                    F('due_date').asc(nulls_last=True), '-created_at'
                )[:5],
                many=True,
            ).data,
        })


# -- Transactions -----------------------------------------------------------------


class TransactionListCreateView(ProjectScopedView):
    """List/filter the ledger, or record a transaction."""

    def get(self, request, project_id):
        project = self.get_project()
        transactions = project.operate_transactions.select_related('invoice')

        kind = request.query_params.get('kind', '').strip()
        if kind in (Transaction.KIND_INCOME, Transaction.KIND_EXPENSE):
            transactions = transactions.filter(kind=kind)
        category = request.query_params.get('category', '').strip()
        if category:
            transactions = transactions.filter(category=category)
        search = request.query_params.get('search', '').strip()
        if search:
            transactions = transactions.filter(
                Q(description__icontains=search) | Q(notes__icontains=search)
            )

        page, total = paginate(request, transactions)
        summary = transactions.aggregate(
            income=Sum('amount', filter=Q(kind=Transaction.KIND_INCOME)),
            expenses=Sum('amount', filter=Q(kind=Transaction.KIND_EXPENSE)),
        )
        income = money(summary['income'])
        expenses = money(summary['expenses'])
        return Response({
            'transactions': TransactionSerializer(page, many=True).data,
            'total': total,
            'summary': {
                'income': income,
                'expenses': expenses,
                'net': round(income - expenses, 2),
            },
        })

    def post(self, request, project_id):
        project = self.get_project()
        serializer = TransactionSerializer(data=request.data, context={'project': project})
        serializer.is_valid(raise_exception=True)
        transaction = serializer.save()
        return Response(
            {'transaction': TransactionSerializer(transaction).data},
            status=status.HTTP_201_CREATED,
        )


class TransactionDetailView(ProjectScopedView):
    """Read, update, or remove a ledger entry."""

    def get_transaction(self, project, pk) -> Transaction:
        try:
            return project.operate_transactions.get(id=pk)
        except Transaction.DoesNotExist:
            raise NotFound('Transaction not found')

    def get(self, request, project_id, pk):
        transaction = self.get_transaction(self.get_project(), pk)
        return Response({'transaction': TransactionSerializer(transaction).data})

    def patch(self, request, project_id, pk):
        project = self.get_project()
        transaction = self.get_transaction(project, pk)
        serializer = TransactionSerializer(
            transaction, data=request.data, partial=True, context={'project': project}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'transaction': TransactionSerializer(transaction).data})

    def delete(self, request, project_id, pk):
        transaction = self.get_transaction(self.get_project(), pk)
        transaction.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -- Invoices ----------------------------------------------------------------------


class InvoiceListCreateView(ProjectScopedView):
    """List invoices, or create a draft (the number is assigned server-side)."""

    def get(self, request, project_id):
        project = self.get_project()
        invoices = project.operate_invoices.all()

        status_filter = request.query_params.get('status', '').strip()
        if status_filter == 'overdue':
            invoices = invoices.filter(
                status=Invoice.STATUS_SENT, due_date__lt=timezone.localdate()
            )
        elif status_filter:
            invoices = invoices.filter(status=status_filter)
        search = request.query_params.get('search', '').strip()
        if search:
            invoices = invoices.filter(
                Q(number__icontains=search)
                | Q(customer_name__icontains=search)
                | Q(customer_email__icontains=search)
            )

        page, total = paginate(request, invoices)
        return Response({
            'invoices': InvoiceSerializer(page, many=True).data,
            'total': total,
        })

    def post(self, request, project_id):
        project = self.get_project()
        serializer = InvoiceSerializer(data=request.data, context={'project': project})
        serializer.is_valid(raise_exception=True)
        invoice = serializer.save()
        return Response(
            {'invoice': InvoiceSerializer(invoice).data},
            status=status.HTTP_201_CREATED,
        )


class InvoiceDetailView(ProjectScopedView):
    """Read an invoice; edit or delete drafts."""

    def get_invoice(self, project, pk) -> Invoice:
        try:
            return project.operate_invoices.get(id=pk)
        except Invoice.DoesNotExist:
            raise NotFound('Invoice not found')

    def get(self, request, project_id, pk):
        invoice = self.get_invoice(self.get_project(), pk)
        return Response({'invoice': InvoiceSerializer(invoice).data})

    def patch(self, request, project_id, pk):
        project = self.get_project()
        invoice = self.get_invoice(project, pk)
        if not invoice.is_editable:
            return Response(
                {'error': 'Only draft invoices can be edited.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = InvoiceSerializer(
            invoice, data=request.data, partial=True, context={'project': project}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'invoice': InvoiceSerializer(invoice).data})

    def delete(self, request, project_id, pk):
        invoice = self.get_invoice(self.get_project(), pk)
        if invoice.status == Invoice.STATUS_PAID:
            return Response(
                {'error': 'Paid invoices cannot be deleted — void them instead.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        invoice.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InvoiceStatusView(ProjectScopedView):
    """
    Move an invoice through its lifecycle: draft -> sent -> paid, with void
    as an off-ramp. Marking an invoice paid records the income in the ledger.
    """

    def post(self, request, project_id, pk):
        project = self.get_project()
        try:
            invoice = project.operate_invoices.get(id=pk)
        except Invoice.DoesNotExist:
            raise NotFound('Invoice not found')

        new_status = str(request.data.get('status', '') or '').strip()
        valid_statuses = {choice for choice, _ in Invoice.STATUS_CHOICES}
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Unknown status "{new_status}".'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not invoice.can_transition_to(new_status):
            return Response(
                {'error': f'A {invoice.get_status_display().lower()} invoice cannot be marked {new_status}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if new_status == Invoice.STATUS_SENT and not invoice.line_items:
            return Response(
                {'error': 'Add at least one line item before sending an invoice.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()
        invoice.status = new_status
        if new_status == Invoice.STATUS_SENT:
            invoice.sent_at = now
        elif new_status == Invoice.STATUS_PAID:
            invoice.paid_at = now
            Transaction.objects.create(
                project=project,
                kind=Transaction.KIND_INCOME,
                category='sales',
                description=f'Invoice {invoice.number} — {invoice.customer_name}',
                amount=invoice.total,
                occurred_on=timezone.localdate(),
                invoice=invoice,
            )
        elif new_status == Invoice.STATUS_DRAFT:
            invoice.sent_at = None
        invoice.save()
        return Response({'invoice': InvoiceSerializer(invoice).data})


# -- Tasks --------------------------------------------------------------------------


class TaskListCreateView(ProjectScopedView):
    """List/filter operational tasks, or add one."""

    def get(self, request, project_id):
        project = self.get_project()
        tasks = project.operate_tasks.all()

        status_filter = request.query_params.get('status', '').strip()
        if status_filter == 'open':
            tasks = tasks.exclude(status=OperationsTask.STATUS_DONE)
        elif status_filter:
            tasks = tasks.filter(status=status_filter)

        page, total = paginate(request, tasks, default_limit=100)
        counts = {
            row['status']: row['count']
            for row in project.operate_tasks.values('status').annotate(count=Count('id'))
        }
        return Response({
            'tasks': OperationsTaskSerializer(page, many=True).data,
            'total': total,
            'counts': {
                'todo': counts.get(OperationsTask.STATUS_TODO, 0),
                'in_progress': counts.get(OperationsTask.STATUS_IN_PROGRESS, 0),
                'done': counts.get(OperationsTask.STATUS_DONE, 0),
            },
        })

    def post(self, request, project_id):
        project = self.get_project()
        serializer = OperationsTaskSerializer(data=request.data, context={'project': project})
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        return Response(
            {'task': OperationsTaskSerializer(task).data},
            status=status.HTTP_201_CREATED,
        )


class TaskDetailView(ProjectScopedView):
    """Read, update, or remove a task. Status changes keep completed_at in sync."""

    def get_task(self, project, pk) -> OperationsTask:
        try:
            return project.operate_tasks.get(id=pk)
        except OperationsTask.DoesNotExist:
            raise NotFound('Task not found')

    def get(self, request, project_id, pk):
        task = self.get_task(self.get_project(), pk)
        return Response({'task': OperationsTaskSerializer(task).data})

    def patch(self, request, project_id, pk):
        project = self.get_project()
        task = self.get_task(project, pk)
        serializer = OperationsTaskSerializer(
            task, data=request.data, partial=True, context={'project': project}
        )
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        if task.status == OperationsTask.STATUS_DONE and task.completed_at is None:
            task.completed_at = timezone.now()
            task.save(update_fields=['completed_at', 'updated_at'])
        elif task.status != OperationsTask.STATUS_DONE and task.completed_at is not None:
            task.completed_at = None
            task.save(update_fields=['completed_at', 'updated_at'])
        return Response({'task': OperationsTaskSerializer(task).data})

    def delete(self, request, project_id, pk):
        task = self.get_task(self.get_project(), pk)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
