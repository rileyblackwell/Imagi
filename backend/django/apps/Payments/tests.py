"""
Tests for the Payments app.

Covers the models, the transaction / payment-method services (pure database
logic, Stripe never touched), the dollar-denominated usage metering, and the
API endpoints. Endpoints that reach Stripe are exercised with the Stripe
service mocked out.
"""

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from apps.Payments.models import (
    PaymentMethod,
    StripeCustomer,
    Subscription,
    Transaction,
    UsageEvent,
)
from apps.Payments.services.payment_method_service import PaymentMethodService
from apps.Payments.services.plans import (
    PLANS,
    get_plan,
    get_plan_for_user,
)
from apps.Payments.services.transaction_service import TransactionService
from apps.Payments.services.usage_service import (
    WEEKLY_WINDOW,
    check_usage_allowed,
    get_usage_status,
    record_usage,
)

User = get_user_model()


def make_user(username='user1', **kwargs):
    return User.objects.create_user(
        username=username,
        email=kwargs.pop('email', f'{username}@example.com'),
        password=kwargs.pop('password', 'correct-horse-9'),
        **kwargs,
    )


def make_transaction(user, amount, **kwargs):
    """A historical purchase row (nothing in the app writes these now)."""
    return Transaction.objects.create(
        user=user,
        amount=Decimal(str(amount)),
        transaction_type=kwargs.pop('transaction_type', 'purchase'),
        status=kwargs.pop('status', 'pending'),
        **kwargs,
    )


# --------------------------------------------------------------------------- #
# Models
# --------------------------------------------------------------------------- #
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
# TransactionService (read-only history)
# --------------------------------------------------------------------------- #
class TransactionServiceTests(APITestCase):
    def setUp(self):
        self.user = make_user()
        self.service = TransactionService()

    def test_get_payment_history_only_returns_completed_purchases(self):
        make_transaction(self.user, 10)  # pending
        done = make_transaction(self.user, 20, status='completed')
        make_transaction(self.user, -5, transaction_type='usage', status='completed')
        history = self.service.get_payment_history(self.user)
        self.assertEqual(list(history), [done])

    def test_get_transactions_filters_by_status(self):
        a = make_transaction(self.user, 10, status='completed')
        make_transaction(self.user, 20)  # pending
        result = self.service.get_transactions(self.user, status='completed')
        self.assertEqual(result['count'], 1)
        self.assertEqual(list(result['transactions']), [a])


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


# --------------------------------------------------------------------------- #
# Plans
# --------------------------------------------------------------------------- #
class PlanRegistryTests(APITestCase):
    def setUp(self):
        self.user = make_user()

    def test_free_is_the_only_plan(self):
        # Paid plans were removed; they come back only as a deliberate change.
        self.assertEqual(list(PLANS), ['free'])

    def test_unknown_plan_falls_back_to_free(self):
        self.assertEqual(get_plan('legacy-gold')['id'], 'free')
        self.assertEqual(get_plan(None)['id'], 'free')

    def test_user_without_subscription_row_is_on_free(self):
        self.assertEqual(get_plan_for_user(self.user)['id'], 'free')

    def test_a_leftover_paid_plan_row_resolves_to_free(self):
        # Rows from the old paid tiers (or anything unknown) get Free's cap.
        for plan_id in ('pro', 'max_5x', 'max_10x', 'max_20x', 'discontinued'):
            Subscription.objects.update_or_create(
                user=self.user, defaults={'plan': plan_id}
            )
            self.assertEqual(get_plan_for_user(self.user)['id'], 'free', plan_id)

    def test_plans_carry_no_figure_the_meter_does_not_enforce(self):
        # The weekly window is the only one checked, so it is the only
        # allowance a plan may advertise. The project limit is enforced at
        # creation (ProjectLimitTests).
        for plan in PLANS.values():
            self.assertEqual(
                set(plan), {'id', 'name', 'weekly_usd', 'max_active_projects'}
            )

    def test_no_plan_limits_projects(self):
        self.assertIsNone(PLANS['free']['max_active_projects'])


# --------------------------------------------------------------------------- #
# Usage metering
# --------------------------------------------------------------------------- #
class RecordUsageTests(APITestCase):
    def setUp(self):
        self.user = make_user()

    def test_records_event_with_total_and_cost(self):
        event = record_usage(
            self.user, 'gpt-5.6-terra', 1000, 200, cost_usd=0.006, conversation_id=7
        )
        self.assertEqual(event.total_tokens, 1200)
        self.assertEqual(event.cost_usd, Decimal('0.006000'))
        self.assertEqual(event.conversation_id, 7)
        self.assertEqual(UsageEvent.objects.count(), 1)

    def test_skips_when_usage_absent(self):
        # Absent usage means unknown, never free: no zero-token rows.
        self.assertIsNone(record_usage(self.user, 'gpt-5.6-terra', None, None))
        self.assertIsNone(record_usage(self.user, 'gpt-5.6-terra', 0, 0))
        self.assertEqual(UsageEvent.objects.count(), 0)

    def test_records_when_only_one_count_present(self):
        event = record_usage(self.user, 'gpt-5.6-terra', 500, None, cost_usd=0.0015)
        self.assertEqual(event.total_tokens, 500)

    def test_unpriced_run_falls_back_to_the_priciest_rate(self):
        # A run we couldn't price must never meter as free — it is charged at
        # the most expensive tier's rate instead (Astra's $10 per M input).
        event = record_usage(self.user, 'mystery-model', 1_000_000, 0)
        self.assertEqual(event.cost_usd, Decimal('10.000000'))

    def test_sub_cent_cost_is_not_rounded_away(self):
        event = record_usage(self.user, 'gpt-5.6-luna', 100, 10, cost_usd=0.00015)
        self.assertEqual(event.cost_usd, Decimal('0.000150'))


class UsageWindowTests(APITestCase):
    def setUp(self):
        self.user = make_user()

    def _event(self, cost, age):
        """Create a usage event of the given cost, backdated by `age`."""
        event = record_usage(self.user, 'gpt-5.6-terra', 1000, 0, cost_usd=cost)
        UsageEvent.objects.filter(pk=event.pk).update(
            created_at=timezone.now() - age
        )
        return UsageEvent.objects.get(pk=event.pk)

    def test_windows_empty_without_events(self):
        status_payload = get_usage_status(self.user)
        for window in status_payload['windows'].values():
            self.assertEqual(window['used_usd'], 0)
            self.assertIsNone(window['resets_at'])
        self.assertEqual(status_payload['plan']['id'], 'free')
        self.assertEqual(
            status_payload['windows']['weekly']['limit_usd'],
            PLANS['free']['weekly_usd'],
        )

    def test_status_reports_what_the_plan_includes(self):
        plan = get_usage_status(self.user)['plan']
        self.assertEqual(plan['id'], 'free')
        self.assertIsNone(plan['max_active_projects'])
        self.assertNotIn('early_access', plan)

    def test_weekly_is_the_only_window(self):
        # The 5-hour session window was removed; nothing may reintroduce a
        # second allowance without this failing.
        self.assertEqual(set(get_usage_status(self.user)['windows']), {'weekly'})

    def test_event_older_than_a_week_counts_nowhere(self):
        self._event(0.10, timedelta(days=7, minutes=1))
        windows = get_usage_status(self.user)['windows']
        self.assertEqual(windows['weekly']['used_usd'], 0)

    def test_used_sums_events_and_resets_at_tracks_oldest(self):
        oldest = self._event(0.10, timedelta(hours=2))
        self._event(0.05, timedelta(hours=1))
        windows = get_usage_status(self.user)['windows']
        self.assertEqual(windows['weekly']['used_usd'], 0.15)
        self.assertEqual(
            windows['weekly']['resets_at'],
            (oldest.created_at + WEEKLY_WINDOW).isoformat(),
        )

    def test_other_users_events_do_not_count(self):
        other = make_user('other')
        record_usage(other, 'gpt-5.6-terra', 9_999, 0, cost_usd=5.0)
        windows = get_usage_status(self.user)['windows']
        self.assertEqual(windows['weekly']['used_usd'], 0)


class FallbackRateTests(APITestCase):
    def test_fallback_is_the_priciest_model(self):
        # An unpriced run must never meter cheaper than any real model.
        from apps.Imagi.Build.services.models_service import MODELS
        from apps.Payments.services.usage_service import (
            FALLBACK_INPUT_PRICE_PER_M,
            FALLBACK_OUTPUT_PRICE_PER_M,
        )
        for model in MODELS.values():
            self.assertGreaterEqual(FALLBACK_INPUT_PRICE_PER_M, Decimal(str(model['input_price_per_m_tokens'])))
            self.assertGreaterEqual(FALLBACK_OUTPUT_PRICE_PER_M, Decimal(str(model['output_price_per_m_tokens'])))
        self.assertEqual(FALLBACK_OUTPUT_PRICE_PER_M, Decimal('50'))


class CheckUsageAllowedTests(APITestCase):
    def setUp(self):
        self.user = make_user()

    def test_allowed_under_allowance(self):
        record_usage(self.user, 'gpt-5.6-terra', 1_000, 0, cost_usd=0.01)
        allowed, payload = check_usage_allowed(self.user)
        self.assertTrue(allowed)
        self.assertEqual(payload['plan']['id'], 'free')

    def test_refused_over_weekly_allowance(self):
        event = record_usage(
            self.user, 'gpt-5.6-terra', 1_000, 0,
            cost_usd=PLANS['free']['weekly_usd'],
        )
        UsageEvent.objects.filter(pk=event.pk).update(
            created_at=timezone.now() - timedelta(days=1)
        )
        allowed, payload = check_usage_allowed(self.user)
        self.assertFalse(allowed)
        self.assertEqual(payload['error'], 'usage_limit_exceeded')
        self.assertEqual(payload['window'], 'week')
        self.assertIsNotNone(payload['resets_at'])
        self.assertIn('detail', payload)
        self.assertNotIn('upgrade', payload['detail'])

    def test_a_leftover_paid_row_gets_free_s_cap(self):
        Subscription.objects.create(user=self.user, plan='max_10x')
        record_usage(
            self.user, 'gpt-5.6-terra', 1_000, 0,
            cost_usd=PLANS['free']['weekly_usd'],
        )
        allowed, payload = check_usage_allowed(self.user)
        self.assertFalse(allowed)
        self.assertEqual(get_usage_status(self.user)['windows']['weekly']['limit_usd'], 20)



class FreeTierWeeklyCapTests(APITestCase):
    """Free: $20 a week of combined Anthropic and OpenAI spend, nothing else."""

    def setUp(self):
        self.user = make_user()

    def test_free_allowance_is_twenty_dollars_a_week(self):
        self.assertEqual(PLANS['free']['weekly_usd'], 20)
        weekly = get_usage_status(self.user)['windows']['weekly']
        self.assertEqual(weekly['limit_usd'], 20)

    def test_the_weekly_allowance_is_free_s_only_limit(self):
        self.assertIsNone(PLANS['free']['max_active_projects'])
        self.assertEqual(set(get_usage_status(self.user)['windows']), {'weekly'})

    def test_every_plan_has_a_weekly_allowance(self):
        # No plan may be unlimited: a missing allowance would let any
        # account run up unbounded API spend.
        for plan in PLANS.values():
            self.assertIsInstance(plan['weekly_usd'], (int, float), plan['id'])
            self.assertGreater(plan['weekly_usd'], 0, plan['id'])

    def test_anthropic_and_openai_spend_share_one_allowance(self):
        record_usage(self.user, 'claude-sonnet-5-5', 1_000, 0, cost_usd=12)
        record_usage(self.user, 'gpt-5.6-terra', 1_000, 0, cost_usd=7)
        allowed, payload = check_usage_allowed(self.user)
        self.assertTrue(allowed)
        self.assertEqual(payload['windows']['weekly']['used_usd'], 19)

        record_usage(self.user, 'gpt-5.6-terra', 1_000, 0, cost_usd=1)
        allowed, payload = check_usage_allowed(self.user)
        self.assertFalse(allowed)
        self.assertEqual(payload['error'], 'usage_limit_exceeded')

    @override_settings(FREE_TIER_UNLIMITED=True)
    def test_the_old_unlimited_switch_no_longer_lifts_the_cap(self):
        record_usage(self.user, 'gpt-5.6-terra', 1_000, 0, cost_usd=25)
        allowed, _ = check_usage_allowed(self.user)
        self.assertFalse(allowed)

    def test_spend_older_than_a_week_frees_up(self):
        event = record_usage(self.user, 'gpt-5.6-terra', 1_000, 0, cost_usd=20)
        UsageEvent.objects.filter(pk=event.pk).update(
            created_at=timezone.now() - timedelta(days=7, minutes=1)
        )
        allowed, _ = check_usage_allowed(self.user)
        self.assertTrue(allowed)


class MoveExistingAccountsToFreeMigrationTests(APITestCase):
    """Migration 0006 puts every existing account on the Free plan."""

    def test_stored_paid_plans_move_to_free(self):
        import importlib
        from django.apps import apps as django_apps

        migration = importlib.import_module(
            'apps.Payments.migrations.0006_move_existing_accounts_to_free'
        )
        for name, plan in (('a', 'pro'), ('b', 'max_5x'), ('c', 'max_10x'), ('d', 'free')):
            Subscription.objects.create(user=make_user(name), plan=plan)
        no_row = make_user('e')

        migration.forwards(django_apps, None)

        self.assertEqual(
            set(Subscription.objects.values_list('plan', flat=True)), {'free'}
        )
        for user in User.objects.all():
            self.assertEqual(get_plan_for_user(user)['id'], 'free')
        self.assertEqual(get_usage_status(no_row)['windows']['weekly']['limit_usd'], 20)

class PaymentsAPITests(APITestCase):
    def setUp(self):
        self.user = make_user()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_usage_endpoint_requires_auth(self):
        self.client.credentials()  # drop auth
        resp = self.client.get(reverse('api-usage-status'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_usage_endpoint_returns_status_and_plan_registry(self):
        record_usage(self.user, 'gpt-5.6-terra', 1_000, 500, cost_usd=0.0105)
        resp = self.client.get(reverse('api-usage-status'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['plan']['id'], 'free')
        self.assertEqual(resp.data['windows']['weekly']['used_usd'], 0.0105)
        # The registry rides along; Free is the only plan.
        self.assertEqual([p['id'] for p in resp.data['plans']], ['free'])
        self.assertEqual(
            resp.data['plans'][0]['weekly_usd'],
            PLANS['free']['weekly_usd'],
        )

    def test_history_endpoint_returns_completed_purchases(self):
        make_transaction(self.user, 15, status='completed')
        resp = self.client.get(reverse('api-payment-history'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data['payments']), 1)
        # PaymentHistorySerializer forces positive amounts for display.
        self.assertEqual(resp.data['payments'][0]['amount'], 15.0)

    def test_transactions_endpoint_scoped_to_user(self):
        other = make_user('intruder')
        make_transaction(other, 99)
        make_transaction(self.user, 15)
        resp = self.client.get(reverse('api-transaction-history'))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['total_count'], 1)

    def test_the_paid_plan_endpoints_are_gone(self):
        # Checkout, plan changes, the billing portal and the subscription
        # webhook went with the paid plans.
        for name in (
            'api-create-checkout-session', 'api-session-status',
            'api-change-plan', 'api-create-portal-session', 'api-stripe-webhook',
        ):
            with self.assertRaises(NoReverseMatch, msg=name):
                reverse(name)
