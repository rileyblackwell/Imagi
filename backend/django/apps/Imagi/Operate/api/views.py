"""
API views for the Operate app.

Everything is scoped to a project owned by the authenticated user:
/api/v1/operate/projects/<project_id>/...

The dashboard endpoint returns Operate's two halves: the app (uptime,
response time, visitors) and the business (revenue, expenses, profit). The
page-view beacon is the one public endpoint: /api/v1/operate/beacon/<key>/.
"""

import json

from django.db.models import Count, Q, Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView

from apps.Imagi.ProjectManager.models import Project

from ..models import AppMonitor, Invoice, OperationsTask, PageView, Transaction
from ..services import monitoring
from ..services.business import business_summary
from .serializers import (
    AppMonitorSerializer,
    InvoiceSerializer,
    OperationsTaskSerializer,
    TransactionSerializer,
)


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


class DashboardView(ProjectScopedView):
    """The two halves of Operate: the app and the business."""

    def get(self, request, project_id):
        project = self.get_project()
        return Response({
            'app': monitoring.app_summary(project),
            'business': business_summary(project),
        })


class AppMonitorView(ProjectScopedView):
    """Read or set the app's live address (and get its page-view tag key)."""

    def get(self, request, project_id):
        project = self.get_project()
        monitor, _ = AppMonitor.objects.get_or_create(project=project)
        return Response(AppMonitorSerializer(monitor).data)

    def patch(self, request, project_id):
        project = self.get_project()
        monitor, _ = AppMonitor.objects.get_or_create(project=project)
        live_url = monitoring.normalize_live_url(str(request.data.get('live_url', '')))
        if live_url:
            if len(live_url) > 500:
                return Response({'live_url': ['That address is too long.']}, status=status.HTTP_400_BAD_REQUEST)
            try:
                monitoring.assert_public_url(live_url)
            except monitoring.UnsafeURL as exc:
                return Response({'live_url': [str(exc)]}, status=status.HTTP_400_BAD_REQUEST)
        monitor.live_url = live_url
        monitor.save(update_fields=['live_url', 'updated_at'])
        if live_url:
            monitoring.run_check(monitor)
        return Response({
            'monitor': AppMonitorSerializer(monitor).data,
            'app': monitoring.app_summary(project),
        })


class UptimeCheckThrottle(UserRateThrottle):
    """"Check now" makes an outbound request; keep it to a human pace."""

    scope = 'operate_uptime_check'
    rate = '12/min'


class UptimeCheckView(ProjectScopedView):
    """Check the live address now (or only if the last check is stale)."""

    throttle_classes = [UptimeCheckThrottle]

    def post(self, request, project_id):
        project = self.get_project()
        monitor = AppMonitor.objects.filter(project=project).first()
        if not monitor or not monitor.live_url:
            return Response(
                {'detail': 'Add your app’s live address first.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        only_if_stale = str(request.data.get('only_if_stale', '')).lower() in ('1', 'true')
        if not only_if_stale or monitoring.check_is_stale(monitor):
            monitoring.run_check(monitor)
        return Response({'app': monitoring.app_summary(project)})


class PageViewBeaconThrottle(AnonRateThrottle):
    """Per-IP cap on the public page-view endpoint."""

    scope = 'operate_beacon'
    rate = '120/min'


# A runaway script on one site shouldn't be able to grow the table without
# bound; past this many views in a day the rest are dropped.
MAX_PAGE_VIEWS_PER_DAY = 50_000


class PageViewBeaconView(APIView):
    """Public endpoint the app's page-view tag posts to on every page load.

    Posted with navigator.sendBeacon as text/plain (so browsers send it
    without a CORS preflight). Always answers 204, so the tag never learns
    whether a view was counted.
    """

    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [PageViewBeaconThrottle]

    def post(self, request, site_key):
        monitor = (
            AppMonitor.objects.select_related('project')
            .filter(site_key=site_key, project__is_active=True)
            .first()
        )
        if monitor and monitor.live_url:
            self.record(request, monitor)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def record(self, request, monitor):
        source = request.headers.get('Origin') or request.headers.get('Referer') or ''
        live_host = monitoring.host_of(monitor.live_url)
        if not monitoring.same_site(monitoring.host_of(source), live_host):
            return
        try:
            payload = json.loads(request.body[:2048] or b'{}')
        except (ValueError, UnicodeDecodeError):
            payload = {}
        if not isinstance(payload, dict):
            payload = {}
        path = str(payload.get('p') or '/')[:300]
        if not path.startswith('/'):
            path = '/'
        referrer_host = monitoring.host_of(str(payload.get('r') or ''))
        if monitoring.same_site(referrer_host, live_host):
            referrer_host = ''

        project = monitor.project
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if project.operate_page_views.filter(created_at__gte=today_start).count() >= MAX_PAGE_VIEWS_PER_DAY:
            return
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
        ip = forwarded.split(',')[0].strip() or request.META.get('REMOTE_ADDR', '')
        PageView.objects.create(
            project=project,
            path=path,
            visitor=monitoring.visitor_hash(
                monitor.site_key, ip, request.headers.get('User-Agent', '')
            ),
            referrer_host=referrer_host[:255],
        )


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
