"""
Tests for the Payments app.

Covers the models, the credit / transaction / payment-method services (all
pure database logic, Stripe never touched), and the API endpoints. Endpoints
that reach Stripe are exercised with the Stripe service mocked out.
"""

from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from apps.Payments.models import (
    CreditBalance,
    CreditPackage,
    Payment,
    PaymentMethod,
    Transaction,
)
from apps.Payments.services.credit_service import CreditService
from apps.Payments.services.payment_method_service import PaymentMethodService
from apps.Payments.services.transaction_service import TransactionService

User = get_user_model()


def make_user(username='user1', **kwargs):
    return User.objects.create_user(
        username=username,
        email=kwargs.pop('email', f'{username}@example.com'),
        password=kwargs.pop('password', 'correct-horse-9'),
        **kwargs,
    )


# --------------------------------------------------------------------------- #
# Models
# --------------------------------------------------------------------------- #
class PaymentModelTests(APITestCase):
    def test_calculate_credits_is_one_to_one(self):
        self.assertEqual(Payment.calculate_credits(25), Decimal('25'))
        self.assertEqual(Payment.calculate_credits('12.50'), Decimal('12.50'))


class TransactionModelTests(APITestCase):
    def setUp(self):
        self.user = make_user()

    def test_purchase_gets_default_description(self):
        txn = Transaction.objects.create(
            user=self.user, amount=Decimal('20'), transaction_type='purchase',
            status='completed',
        )
        self.assertIn('Credit purchase', txn.description)

    def test_usage_gets_default_description(self):
        txn = Transaction.objects.create(
            user=self.user, amount=Decimal('-5'), transaction_type='usage',
            status='completed',
        )
        self.assertIn('Usage', txn.description)

    def test_explicit_description_is_preserved(self):
        txn = Transaction.objects.create(
            user=self.user, amount=Decimal('20'), transaction_type='purchase',
            status='completed', description='Custom note',
        )
        self.assertEqual(txn.description, 'Custom note')


class PaymentMethodModelTests(APITestCase):
    def setUp(self):
        self.user = make_user()

    def _make(self, pm_id, is_default=False):
        return PaymentMethod.objects.create(
            user=self.user, payment_method_id=pm_id, card_brand='visa',
            last4='4242', exp_month=12, exp_year=2030, is_default=is_default,
        )

    def test_setting_new_default_clears_previous_default(self):
        first = self._make('pm_1', is_default=True)
        second = self._make('pm_2', is_default=True)
        first.refresh_from_db()
        second.refresh_from_db()
        self.assertFalse(first.is_default)
        self.assertTrue(second.is_default)


# --------------------------------------------------------------------------- #
# CreditService
# --------------------------------------------------------------------------- #
class CreditServiceTests(APITestCase):
    def setUp(self):
        self.user = make_user()
        self.service = CreditService()

    def test_get_balance_creates_zero_balance(self):
        self.assertEqual(self.service.get_balance(self.user), 0.0)
        self.assertTrue(CreditBalance.objects.filter(user=self.user).exists())

    def test_add_credits_increases_balance(self):
        result = self.service.add_credits(self.user, 30.0)
        self.assertTrue(result['success'])
        self.assertEqual(result['new_balance'], 30.0)
        self.assertEqual(self.service.get_balance(self.user), 30.0)

    def test_add_credits_marks_transaction_completed(self):
        txn = Transaction.objects.create(
            user=self.user, amount=Decimal('30'), transaction_type='purchase',
            status='pending',
        )
        self.service.add_credits(self.user, 30.0, txn)
        txn.refresh_from_db()
        self.assertEqual(txn.status, 'completed')

    def test_deduct_credits_reduces_balance_and_records_usage(self):
        self.service.add_credits(self.user, 50.0)
        result = self.service.deduct_credits(self.user, 20.0, 'Model run')
        self.assertTrue(result['success'])
        self.assertAlmostEqual(result['new_balance'], 30.0, places=2)
        # A negative usage transaction should have been recorded.
        usage = Transaction.objects.filter(user=self.user, transaction_type='usage')
        self.assertEqual(usage.count(), 1)
        self.assertEqual(usage.first().amount, Decimal('-20.0'))

    def test_deduct_more_than_balance_fails(self):
        self.service.add_credits(self.user, 5.0)
        result = self.service.deduct_credits(self.user, 20.0)
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'Insufficient credits')
        # Balance is untouched.
        self.assertEqual(self.service.get_balance(self.user), 5.0)

    def test_deduct_non_positive_amount_fails(self):
        result = self.service.deduct_credits(self.user, 0)
        self.assertFalse(result['success'])

    def test_check_credits_reports_sufficiency(self):
        self.service.add_credits(self.user, 10.0)
        ok = self.service.check_credits(self.user, 5.0)
        self.assertTrue(ok['has_sufficient'])
        short = self.service.check_credits(self.user, 25.0)
        self.assertFalse(short['has_sufficient'])
        self.assertAlmostEqual(short['needed_credits'], 15.0, places=2)


# --------------------------------------------------------------------------- #
# TransactionService
# --------------------------------------------------------------------------- #
class TransactionServiceTests(APITestCase):
    def setUp(self):
        self.user = make_user()
        self.service = TransactionService()

    def test_create_purchase_transaction(self):
        txn = self.service.create_purchase_transaction(
            self.user, 40.0, stripe_payment_intent_id='pi_123'
        )
        self.assertEqual(txn.transaction_type, 'purchase')
        self.assertEqual(txn.status, 'pending')
        self.assertEqual(txn.stripe_payment_intent_id, 'pi_123')

    def test_create_usage_transaction_stores_negative_amount(self):
        txn = self.service.create_usage_transaction(self.user, 3.0)
        self.assertIsNotNone(txn)
        self.assertEqual(txn.amount, Decimal('-3.0'))
        self.assertEqual(txn.transaction_type, 'usage')

    def test_get_payment_history_only_returns_completed_purchases(self):
        self.service.create_purchase_transaction(self.user, 10.0)  # pending
        done = self.service.create_purchase_transaction(self.user, 20.0)
        done.status = 'completed'
        done.save()
        self.service.create_usage_transaction(self.user, 5.0)  # usage
        history = self.service.get_payment_history(self.user)
        self.assertEqual(list(history), [done])

    def test_get_transactions_filters_by_status(self):
        a = self.service.create_purchase_transaction(self.user, 10.0)
        a.status = 'completed'
        a.save()
        self.service.create_purchase_transaction(self.user, 20.0)  # pending
        result = self.service.get_transactions(self.user, status='completed')
        self.assertEqual(result['count'], 1)
        self.assertEqual(list(result['transactions']), [a])

    def test_lookup_by_payment_intent(self):
        txn = self.service.create_purchase_transaction(
            self.user, 10.0, stripe_payment_intent_id='pi_abc'
        )
        found = self.service.get_transaction_by_payment_intent(self.user, 'pi_abc')
        self.assertEqual(found, txn)
        self.assertIsNone(
            self.service.get_transaction_by_payment_intent(self.user, 'pi_missing')
        )

    def test_get_credit_packages_excludes_inactive_by_default(self):
        CreditPackage.objects.create(
            id='starter', name='Starter', amount=Decimal('10'),
            credits=Decimal('10'), is_active=True,
        )
        CreditPackage.objects.create(
            id='legacy', name='Legacy', amount=Decimal('5'),
            credits=Decimal('5'), is_active=False,
        )
        packages = self.service.get_credit_packages()
        self.assertEqual([p.id for p in packages], ['starter'])
        self.assertEqual(len(self.service.get_credit_packages(include_inactive=True)), 2)


# --------------------------------------------------------------------------- #
# PaymentMethodService
# --------------------------------------------------------------------------- #
class PaymentMethodServiceTests(APITestCase):
    def setUp(self):
        self.user = make_user()
        self.service = PaymentMethodService()

    def test_stripe_customer_id_round_trip(self):
        self.assertIsNone(self.service.get_stripe_customer_id(self.user))
        self.assertTrue(self.service.set_stripe_customer_id(self.user, 'cus_1'))
        self.assertEqual(self.service.get_stripe_customer_id(self.user), 'cus_1')

    def test_first_payment_method_becomes_default(self):
        pm = self.service.create_payment_method(self.user, {
            'payment_method_id': 'pm_1', 'card_brand': 'visa',
            'last4': '4242', 'exp_month': 12, 'exp_year': 2030,
        })
        self.assertTrue(pm.is_default)

    def test_set_default_payment_method(self):
        self.service.create_payment_method(self.user, {
            'payment_method_id': 'pm_1', 'card_brand': 'visa',
            'last4': '4242', 'exp_month': 12, 'exp_year': 2030,
        })
        self.service.create_payment_method(self.user, {
            'payment_method_id': 'pm_2', 'card_brand': 'amex',
            'last4': '0005', 'exp_month': 1, 'exp_year': 2031,
        })
        self.assertTrue(self.service.set_default_payment_method(self.user, 'pm_2'))
        self.assertEqual(
            self.service.get_default_payment_method(self.user).payment_method_id, 'pm_2'
        )

    def test_delete_default_reassigns_default(self):
        self.service.create_payment_method(self.user, {
            'payment_method_id': 'pm_1', 'card_brand': 'visa',
            'last4': '4242', 'exp_month': 12, 'exp_year': 2030,
        })
        self.service.create_payment_method(self.user, {
            'payment_method_id': 'pm_2', 'card_brand': 'amex',
            'last4': '0005', 'exp_month': 1, 'exp_year': 2031,
        })
        # pm_1 is the default; deleting it should promote pm_2.
        self.assertTrue(self.service.delete_payment_method(self.user, 'pm_1'))
        remaining = self.service.get_payment_methods(self.user)
        self.assertEqual(len(remaining), 1)
        self.assertTrue(remaining[0].is_default)

    def test_delete_missing_payment_method_returns_false(self):
        self.assertFalse(self.service.delete_payment_method(self.user, 'pm_missing'))


# --------------------------------------------------------------------------- #
# API endpoints
# --------------------------------------------------------------------------- #
class PaymentsAPITests(APITestCase):
    def setUp(self):
        self.user = make_user()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_balance_endpoint_requires_auth(self):
        self.client.credentials()  # drop auth
        resp = self.client.get(reverse('api-credit-balance'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_balance_endpoint_returns_balance(self):
        CreditService().add_credits(self.user, 42.0)
        resp = self.client.get(reverse('api-credit-balance'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['balance'], 42.0)

    def test_check_credits_endpoint(self):
        CreditService().add_credits(self.user, 10.0)
        resp = self.client.post(
            reverse('api-check-credits'), {'required_credits': 5}
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data['has_sufficient'])

    def test_deduct_credits_endpoint_success(self):
        CreditService().add_credits(self.user, 10.0)
        resp = self.client.post(
            reverse('api-deduct-credits'), {'credits': 4, 'description': 'run'}
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertAlmostEqual(resp.data['new_balance'], 6.0, places=2)

    def test_deduct_credits_insufficient_returns_402(self):
        CreditService().add_credits(self.user, 1.0)
        resp = self.client.post(reverse('api-deduct-credits'), {'credits': 5})
        self.assertEqual(resp.status_code, status.HTTP_402_PAYMENT_REQUIRED)

    def test_packages_endpoint(self):
        CreditPackage.objects.create(
            id='starter', name='Starter', amount=Decimal('10'),
            credits=Decimal('10'), is_active=True,
        )
        resp = self.client.get(reverse('api-credit-packages'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data['packages']), 1)

    def test_history_endpoint_returns_completed_purchases(self):
        svc = TransactionService()
        done = svc.create_purchase_transaction(self.user, 15.0)
        done.status = 'completed'
        done.save()
        resp = self.client.get(reverse('api-payment-history'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data['payments']), 1)
        # PaymentHistorySerializer forces positive amounts for display.
        self.assertEqual(resp.data['payments'][0]['amount'], 15.0)

    def test_transactions_endpoint_scoped_to_user(self):
        other = make_user('intruder')
        TransactionService().create_purchase_transaction(other, 99.0)
        TransactionService().create_purchase_transaction(self.user, 15.0)
        resp = self.client.get(reverse('api-transaction-history'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['total_count'], 1)

    @patch('apps.Payments.api.views.stripe_service')
    def test_process_payment_adds_credits_on_success(self, mock_stripe):
        intent = MagicMock()
        intent.id = 'pi_success'
        intent.status = 'succeeded'
        intent.client_secret = 'secret_123'
        mock_stripe.create_direct_payment.return_value = intent

        resp = self.client.post(reverse('api-process-payment'), {
            'amount': 20, 'paymentMethodId': 'pm_card',
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data['success'])
        self.assertEqual(resp.data['new_balance'], 20.0)
        self.assertEqual(CreditService().get_balance(self.user), 20.0)

    def test_process_payment_requires_amount_and_method(self):
        resp = self.client.post(reverse('api-process-payment'), {'amount': 20})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
