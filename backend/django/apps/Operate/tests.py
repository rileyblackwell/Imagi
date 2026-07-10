"""
Tests for the Operate app: ledger transactions, the invoice lifecycle
(including the paid -> ledger entry hook), operational tasks, and the
central-hub dashboard.
"""

import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase

from apps.Products.Imagi.ProjectManager.models import Project

from .models import Invoice, OperationsTask, Transaction

User = get_user_model()


class OperateAPITestCase(APITestCase):
    """Shared fixtures: a user, their project, and an authenticated client."""

    def setUp(self):
        self.user = User.objects.create_user(username='owner', password='pass12345')
        self.other_user = User.objects.create_user(username='intruder', password='pass12345')
        self.project = Project.objects.create(name='Bloom Coffee', user=self.user)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.base = f'/api/v1/operate/projects/{self.project.id}'

    def add_transaction(self, kind='income', category='sales', amount='100.00',
                        description='Test entry', days_ago=0, **kwargs):
        return Transaction.objects.create(
            project=self.project,
            kind=kind,
            category=category,
            description=description,
            amount=Decimal(amount),
            occurred_on=timezone.localdate() - datetime.timedelta(days=days_ago),
            **kwargs,
        )

    def add_invoice(self, status=Invoice.STATUS_DRAFT, total_price='250.00', **kwargs):
        invoice = Invoice(
            project=self.project,
            number=Invoice.next_number(self.project),
            customer_name=kwargs.pop('customer_name', 'Ada Lovelace'),
            status=status,
            line_items=kwargs.pop('line_items', [
                {'description': 'Consulting', 'quantity': '1', 'unit_price': total_price},
            ]),
            **kwargs,
        )
        invoice.save()
        return invoice


class ProjectScopingTests(OperateAPITestCase):

    def test_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(f'{self.base}/dashboard/')
        self.assertIn(response.status_code, (401, 403))

    def test_other_users_project_is_not_found(self):
        self.client.force_authenticate(user=self.other_user)
        for url in (f'{self.base}/dashboard/', f'{self.base}/transactions/',
                    f'{self.base}/invoices/', f'{self.base}/tasks/'):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404, url)

    def test_inactive_project_is_not_found(self):
        self.project.is_active = False
        self.project.save()
        response = self.client.get(f'{self.base}/dashboard/')
        self.assertEqual(response.status_code, 404)


class TransactionTests(OperateAPITestCase):

    def test_create_income(self):
        response = self.client.post(f'{self.base}/transactions/', {
            'kind': 'income',
            'category': 'sales',
            'description': 'Latte sales',
            'amount': '125.50',
            'occurred_on': str(timezone.localdate()),
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['transaction']['description'], 'Latte sales')
        self.assertEqual(Transaction.objects.count(), 1)

    def test_category_must_match_kind(self):
        response = self.client.post(f'{self.base}/transactions/', {
            'kind': 'income',
            'category': 'rent',
            'description': 'Nope',
            'amount': '10.00',
            'occurred_on': str(timezone.localdate()),
        }, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('category', response.data)

    def test_amount_must_be_positive(self):
        response = self.client.post(f'{self.base}/transactions/', {
            'kind': 'expense',
            'category': 'supplies',
            'description': 'Beans',
            'amount': '-5.00',
            'occurred_on': str(timezone.localdate()),
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_list_includes_filtered_summary(self):
        self.add_transaction(kind='income', category='sales', amount='300.00')
        self.add_transaction(kind='expense', category='supplies', amount='120.00')
        response = self.client.get(f'{self.base}/transactions/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total'], 2)
        self.assertEqual(response.data['summary']['income'], 300.0)
        self.assertEqual(response.data['summary']['expenses'], 120.0)
        self.assertEqual(response.data['summary']['net'], 180.0)

        response = self.client.get(f'{self.base}/transactions/', {'kind': 'income'})
        self.assertEqual(response.data['total'], 1)
        self.assertEqual(response.data['summary']['expenses'], 0.0)

    def test_search_filters_description(self):
        self.add_transaction(description='Espresso machine repair')
        self.add_transaction(description='Website hosting')
        response = self.client.get(f'{self.base}/transactions/', {'search': 'espresso'})
        self.assertEqual(response.data['total'], 1)

    def test_update_and_delete(self):
        transaction = self.add_transaction()
        url = f'{self.base}/transactions/{transaction.id}/'
        response = self.client.patch(url, {'description': 'Renamed'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['transaction']['description'], 'Renamed')

        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Transaction.objects.count(), 0)

    def test_cannot_touch_other_projects_transaction(self):
        other_project = Project.objects.create(name='Other', user=self.other_user)
        foreign = Transaction.objects.create(
            project=other_project, kind='income', category='sales',
            description='Not yours', amount=Decimal('10.00'),
            occurred_on=timezone.localdate(),
        )
        response = self.client.get(f'{self.base}/transactions/{foreign.id}/')
        self.assertEqual(response.status_code, 404)


class InvoiceTests(OperateAPITestCase):

    def create_invoice_via_api(self, **overrides):
        payload = {
            'customer_name': 'Ada Lovelace',
            'customer_email': 'ada@example.com',
            'issue_date': str(timezone.localdate()),
            'due_date': str(timezone.localdate() + datetime.timedelta(days=14)),
            'line_items': [
                {'description': 'Consulting', 'quantity': 2, 'unit_price': '150.00'},
                {'description': 'Support', 'quantity': 1, 'unit_price': '50.00'},
            ],
            **overrides,
        }
        return self.client.post(f'{self.base}/invoices/', payload, format='json')

    def test_create_assigns_number_and_total(self):
        response = self.create_invoice_via_api()
        self.assertEqual(response.status_code, 201)
        invoice = response.data['invoice']
        self.assertEqual(invoice['number'], 'INV-0001')
        self.assertEqual(Decimal(invoice['total']), Decimal('350.00'))
        self.assertEqual(invoice['status'], 'draft')

        response = self.create_invoice_via_api()
        self.assertEqual(response.data['invoice']['number'], 'INV-0002')

    def test_numbering_survives_deletion(self):
        first = self.create_invoice_via_api().data['invoice']
        second = self.create_invoice_via_api().data['invoice']
        self.assertEqual([first['number'], second['number']], ['INV-0001', 'INV-0002'])

        # Deleting an earlier invoice must not make the next number collide
        # with a survivor.
        response = self.client.delete(f"{self.base}/invoices/{first['id']}/")
        self.assertEqual(response.status_code, 204)
        third = self.create_invoice_via_api()
        self.assertEqual(third.status_code, 201)
        self.assertEqual(third.data['invoice']['number'], 'INV-0003')

    def test_round_quantities_stay_in_plain_notation(self):
        # Decimal normalize() would render 10 as '1E+1'.
        response = self.create_invoice_via_api(line_items=[
            {'description': 'Bulk beans', 'quantity': 10, 'unit_price': '5.00'},
        ])
        self.assertEqual(response.status_code, 201)
        item = response.data['invoice']['line_items'][0]
        self.assertEqual(item['quantity'], '10')
        self.assertEqual(Decimal(response.data['invoice']['total']), Decimal('50.00'))

    def test_line_items_are_validated(self):
        response = self.create_invoice_via_api(line_items=[
            {'description': '', 'quantity': 1, 'unit_price': '10.00'},
        ])
        self.assertEqual(response.status_code, 400)

        response = self.create_invoice_via_api(line_items=[
            {'description': 'Bad qty', 'quantity': 0, 'unit_price': '10.00'},
        ])
        self.assertEqual(response.status_code, 400)

    def test_due_date_cannot_precede_issue_date(self):
        response = self.create_invoice_via_api(
            due_date=str(timezone.localdate() - datetime.timedelta(days=1))
        )
        self.assertEqual(response.status_code, 400)

    def test_only_drafts_can_be_edited(self):
        invoice = self.add_invoice(status=Invoice.STATUS_SENT)
        response = self.client.patch(
            f'{self.base}/invoices/{invoice.id}/',
            {'customer_name': 'New name'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)

    def test_lifecycle_sent_then_paid_records_income(self):
        invoice = self.add_invoice(total_price='250.00')
        status_url = f'{self.base}/invoices/{invoice.id}/status/'

        response = self.client.post(status_url, {'status': 'sent'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['invoice']['status'], 'sent')
        self.assertIsNotNone(response.data['invoice']['sent_at'])

        response = self.client.post(status_url, {'status': 'paid'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['invoice']['status'], 'paid')

        ledger = Transaction.objects.get(invoice=invoice)
        self.assertEqual(ledger.kind, Transaction.KIND_INCOME)
        self.assertEqual(ledger.amount, Decimal('250.00'))
        self.assertIn(invoice.number, ledger.description)

    def test_invalid_transitions_are_rejected(self):
        invoice = self.add_invoice()
        status_url = f'{self.base}/invoices/{invoice.id}/status/'

        # draft -> paid skips "sent"
        response = self.client.post(status_url, {'status': 'paid'}, format='json')
        self.assertEqual(response.status_code, 400)

        # paid is terminal
        invoice.status = Invoice.STATUS_PAID
        invoice.save()
        response = self.client.post(status_url, {'status': 'void'}, format='json')
        self.assertEqual(response.status_code, 400)

        response = self.client.post(status_url, {'status': 'nonsense'}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_sending_requires_line_items(self):
        invoice = self.add_invoice(line_items=[])
        response = self.client.post(
            f'{self.base}/invoices/{invoice.id}/status/', {'status': 'sent'}, format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_paid_invoices_cannot_be_deleted(self):
        invoice = self.add_invoice(status=Invoice.STATUS_PAID)
        response = self.client.delete(f'{self.base}/invoices/{invoice.id}/')
        self.assertEqual(response.status_code, 400)

        invoice.status = Invoice.STATUS_DRAFT
        invoice.save()
        response = self.client.delete(f'{self.base}/invoices/{invoice.id}/')
        self.assertEqual(response.status_code, 204)

    def test_overdue_filter_and_flag(self):
        overdue = self.add_invoice(
            status=Invoice.STATUS_SENT,
            due_date=timezone.localdate() - datetime.timedelta(days=3),
        )
        self.add_invoice(
            status=Invoice.STATUS_SENT,
            due_date=timezone.localdate() + datetime.timedelta(days=3),
        )
        response = self.client.get(f'{self.base}/invoices/', {'status': 'overdue'})
        self.assertEqual(response.data['total'], 1)
        self.assertEqual(response.data['invoices'][0]['id'], overdue.id)
        self.assertTrue(response.data['invoices'][0]['is_overdue'])


class TaskTests(OperateAPITestCase):

    def test_create_and_counts(self):
        response = self.client.post(f'{self.base}/tasks/', {
            'title': 'Order more beans',
            'priority': 'high',
        }, format='json')
        self.assertEqual(response.status_code, 201)

        OperationsTask.objects.create(
            project=self.project, title='Done thing', status=OperationsTask.STATUS_DONE
        )
        response = self.client.get(f'{self.base}/tasks/')
        self.assertEqual(response.data['counts'], {'todo': 1, 'in_progress': 0, 'done': 1})

        response = self.client.get(f'{self.base}/tasks/', {'status': 'open'})
        self.assertEqual(response.data['total'], 1)

    def test_completing_a_task_stamps_completed_at(self):
        task = OperationsTask.objects.create(project=self.project, title='Ship orders')
        url = f'{self.base}/tasks/{task.id}/'

        response = self.client.patch(url, {'status': 'done'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data['task']['completed_at'])

        response = self.client.patch(url, {'status': 'todo'}, format='json')
        self.assertIsNone(response.data['task']['completed_at'])

    def test_overdue_flag(self):
        task = OperationsTask.objects.create(
            project=self.project,
            title='Late thing',
            due_date=timezone.localdate() - datetime.timedelta(days=1),
        )
        response = self.client.get(f'{self.base}/tasks/{task.id}/')
        self.assertTrue(response.data['task']['is_overdue'])


class DashboardTests(OperateAPITestCase):

    def test_dashboard_aggregates(self):
        self.add_transaction(kind='income', category='sales', amount='500.00', days_ago=5)
        self.add_transaction(kind='expense', category='supplies', amount='200.00', days_ago=10)
        # Outside the 30-day window; still counts toward all-time.
        self.add_transaction(kind='income', category='services', amount='999.00', days_ago=45)

        self.add_invoice(
            status=Invoice.STATUS_SENT,
            total_price='300.00',
            due_date=timezone.localdate() - datetime.timedelta(days=2),
        )
        OperationsTask.objects.create(
            project=self.project,
            title='Overdue task',
            due_date=timezone.localdate() - datetime.timedelta(days=1),
        )

        response = self.client.get(f'{self.base}/dashboard/')
        self.assertEqual(response.status_code, 200)

        finance = response.data['finance']
        self.assertEqual(finance['income_30d'], 500.0)
        self.assertEqual(finance['expenses_30d'], 200.0)
        self.assertEqual(finance['net_30d'], 300.0)
        self.assertEqual(finance['income_all_time'], 1499.0)

        invoices = response.data['invoices']
        self.assertEqual(invoices['outstanding_total'], 300.0)
        self.assertEqual(invoices['outstanding_count'], 1)
        self.assertEqual(invoices['overdue_count'], 1)

        tasks = response.data['tasks']
        self.assertEqual(tasks['open_count'], 1)
        self.assertEqual(tasks['overdue_count'], 1)

        # Cross-module pulse and hub lists are present.
        self.assertIn('marketing', response.data)
        self.assertFalse(response.data['marketing']['configured'])
        self.assertIn('sell', response.data)
        self.assertFalse(response.data['sell']['configured'])
        self.assertEqual(response.data['sell']['revenue_30d'], 0.0)
        self.assertEqual(len(response.data['recent_transactions']), 3)
        self.assertEqual(len(response.data['open_invoices']), 1)
        self.assertEqual(len(response.data['upcoming_tasks']), 1)

    def test_sell_pulse_counts_paid_orders(self):
        from apps.Sell.models import Order

        Order.objects.create(
            project=self.project,
            status=Order.STATUS_PAID,
            amount_total_cents=12550,
            paid_at=timezone.now() - datetime.timedelta(days=3),
        )
        Order.objects.create(project=self.project, status=Order.STATUS_PENDING)
        response = self.client.get(f'{self.base}/dashboard/')
        sell = response.data['sell']
        self.assertEqual(sell['orders_paid_30d'], 1)
        self.assertEqual(sell['orders_pending'], 1)
        self.assertEqual(sell['revenue_30d'], 125.5)

    def test_cashflow_series_shape(self):
        self.add_transaction(kind='income', category='sales', amount='100.00')
        response = self.client.get(f'{self.base}/dashboard/')
        series = response.data['cashflow']
        self.assertEqual(len(series), 6)
        current = series[-1]
        self.assertEqual(current['month'], timezone.localdate().strftime('%Y-%m'))
        self.assertEqual(current['income'], 100.0)
        self.assertEqual(current['net'], 100.0)
