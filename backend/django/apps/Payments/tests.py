"""
Tests for the Payments app.

Covers the models, the transaction / payment-method services (pure database
logic, Stripe never touched), the dollar-denominated usage metering, and the
API endpoints. Endpoints that reach Stripe are exercised with the Stripe
service mocked out.
"""

from datetime import timedelta
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
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
    has_early_access,
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

    def test_unknown_plan_falls_back_to_free(self):
        self.assertEqual(get_plan('legacy-gold')['id'], 'free')
        self.assertEqual(get_plan(None)['id'], 'free')

    def test_user_without_subscription_row_is_on_free(self):
        self.assertEqual(get_plan_for_user(self.user)['id'], 'free')

    def test_user_subscription_row_selects_plan(self):
        Subscription.objects.create(user=self.user, plan='max_5x')
        self.assertEqual(get_plan_for_user(self.user)['id'], 'max_5x')

    def test_retired_max_20x_id_resolves_to_max_10x(self):
        # Rows written before the $200 tier became 10x keep their allowance.
        Subscription.objects.create(user=self.user, plan='max_20x')
        self.assertEqual(get_plan_for_user(self.user)['id'], 'max_10x')

    def test_old_max_20x_lookup_key_resolves_to_max_10x(self):
        from apps.Payments.services.plans import plan_id_for_lookup_key
        self.assertEqual(plan_id_for_lookup_key('max_20x_monthly'), 'max_10x')
        self.assertEqual(plan_id_for_lookup_key('max_10x_monthly'), 'max_10x')

    def test_stale_subscription_plan_falls_back_to_free(self):
        Subscription.objects.create(user=self.user, plan='discontinued')
        self.assertEqual(get_plan_for_user(self.user)['id'], 'free')

    def test_weekly_allowances_are_the_advertised_dollar_figures(self):
        self.assertEqual(PLANS['free']['weekly_usd'], 3)
        self.assertEqual(PLANS['pro']['weekly_usd'], 10)
        self.assertEqual(PLANS['max_5x']['weekly_usd'], 50)
        self.assertEqual(PLANS['max_10x']['weekly_usd'], 100)

    def test_allowances_rise_with_the_tier(self):
        # A pricier plan must never buy a smaller allowance.
        weekly = [PLANS[p]['weekly_usd'] for p in ('free', 'pro', 'max_5x', 'max_10x')]
        self.assertEqual(weekly, sorted(weekly))
        self.assertEqual(len(set(weekly)), len(weekly))

    def test_max_tier_names_state_their_real_multiple_of_pro(self):
        # The Max tiers are named for what they give you, so the names have to
        # keep matching the allowances.
        pro = PLANS['pro']['weekly_usd']
        self.assertEqual(PLANS['max_5x']['name'], 'Max (5x)')
        self.assertEqual(PLANS['max_5x']['weekly_usd'], 5 * pro)
        self.assertEqual(PLANS['max_10x']['name'], 'Max (10x)')
        self.assertEqual(PLANS['max_10x']['weekly_usd'], 10 * pro)

    def test_plans_carry_no_figure_the_meter_does_not_enforce(self):
        # The weekly window is the only one checked, so it is the only
        # allowance a plan may advertise — a monthly or per-session figure
        # would be a number we publish but never enforce. The project limit
        # is enforced at creation (ProjectLimitTests); early access is a
        # capability flag, not an allowance.
        for plan in PLANS.values():
            self.assertEqual(
                set(plan), {'id', 'name', 'weekly_usd', 'max_active_projects', 'early_access'}
            )

    def test_only_free_limits_projects(self):
        self.assertEqual(PLANS['free']['max_active_projects'], 1)
        for plan_id in ('pro', 'max_5x', 'max_10x'):
            self.assertIsNone(PLANS[plan_id]['max_active_projects'])

    def test_only_max_gets_early_access(self):
        self.assertFalse(PLANS['free']['early_access'])
        self.assertFalse(PLANS['pro']['early_access'])
        self.assertTrue(PLANS['max_5x']['early_access'])
        self.assertTrue(PLANS['max_10x']['early_access'])

    def test_has_early_access_follows_the_users_plan(self):
        user = make_user('early')
        self.assertFalse(has_early_access(user))
        Subscription.objects.create(user=user, plan='pro')
        self.assertFalse(has_early_access(user))
        Subscription.objects.filter(user=user).update(plan='max_5x')
        self.assertTrue(has_early_access(user))
        # A subscriber still on the retired max_20x id keeps the Max perk.
        Subscription.objects.filter(user=user).update(plan='max_20x')
        self.assertTrue(has_early_access(user))


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
        self.assertEqual(plan['max_active_projects'], 1)
        self.assertFalse(plan['early_access'])
        Subscription.objects.create(user=self.user, plan='max_10x')
        plan = get_usage_status(self.user)['plan']
        self.assertIsNone(plan['max_active_projects'])
        self.assertTrue(plan['early_access'])

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

    def test_higher_plan_raises_the_allowance(self):
        Subscription.objects.create(user=self.user, plan='pro')
        record_usage(
            self.user, 'gpt-5.6-terra', 1_000, 0,
            cost_usd=PLANS['free']['weekly_usd'],
        )
        allowed, _ = check_usage_allowed(self.user)
        self.assertTrue(allowed)

    def test_top_max_allowance_far_exceeds_pro(self):
        # A spend that exhausts Pro's week barely dents the top Max tier's.
        Subscription.objects.create(user=self.user, plan='max_10x')
        event = record_usage(
            self.user, 'gpt-5.6-sol', 1_000, 0,
            cost_usd=PLANS['pro']['weekly_usd'],
        )
        UsageEvent.objects.filter(pk=event.pk).update(
            created_at=timezone.now() - timedelta(days=1)
        )
        allowed, payload = check_usage_allowed(self.user)
        self.assertTrue(allowed)
        weekly = payload['windows']['weekly']
        self.assertEqual(weekly['limit_usd'], PLANS['max_10x']['weekly_usd'])
        self.assertGreater(weekly['limit_usd'], PLANS['pro']['weekly_usd'])


# --------------------------------------------------------------------------- #
# Subscription webhook events
# --------------------------------------------------------------------------- #
class SubscriptionWebhookTests(APITestCase):
    """customer.subscription.* events sync the local Subscription row."""

    def setUp(self):
        self.user = make_user()
        StripeCustomer.objects.create(user=self.user, stripe_customer_id='cus_42')
        self.url = reverse('api-stripe-webhook')

    def _post_event(self, event_type, subscription):
        event = SimpleNamespace(
            type=event_type, data=SimpleNamespace(object=subscription)
        )
        # A signing secret must be configured for the webhook to run at all —
        # see test_webhook_without_signing_secret_is_rejected.
        with override_settings(STRIPE_WEBHOOK_SECRET='whsec_test'):
            with patch('apps.Payments.api.views.stripe_service') as mock_stripe:
                mock_stripe.verify_webhook_event.return_value = event
                return self.client.post(self.url, {}, HTTP_STRIPE_SIGNATURE='sig')

    def test_webhook_without_signing_secret_is_rejected(self):
        """No STRIPE_WEBHOOK_SECRET means no verifiable signature, so no event.

        Stripe's library HMACs with whatever key it is handed, including an
        empty one, so an unset secret would leave this unauthenticated,
        plan-granting endpoint forgeable by anyone. It must fail closed.
        """
        event = SimpleNamespace(
            type='customer.subscription.created',
            data=SimpleNamespace(object=self._subscription(lookup_key='max_10x_monthly')),
        )
        with override_settings(STRIPE_WEBHOOK_SECRET=''):
            with patch('apps.Payments.api.views.stripe_service') as mock_stripe:
                mock_stripe.verify_webhook_event.return_value = event
                resp = self.client.post(self.url, {}, HTTP_STRIPE_SIGNATURE='sig')

        self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        # And crucially, no plan was granted.
        self.assertFalse(Subscription.objects.filter(user=self.user).exists())
        mock_stripe.verify_webhook_event.assert_not_called()

    def _subscription(self, lookup_key=None, metadata=None, customer='cus_42',
                      sub_id='sub_1', sub_status='active'):
        price = {'lookup_key': lookup_key} if lookup_key else {}
        return {
            'id': sub_id,
            'customer': customer,
            'status': sub_status,
            'items': {'data': [{'price': price}]},
            'metadata': metadata or {},
        }

    def test_created_event_sets_plan_from_lookup_key(self):
        # The Stripe price lookup_keys the frontend checks out by resolve to
        # their registry plan ids (pro_monthly -> pro, max_*x_monthly -> max_*x).
        resp = self._post_event(
            'customer.subscription.created',
            self._subscription(lookup_key='pro_monthly'),
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.subscription.plan, 'pro')
        self.assertEqual(self.user.subscription.stripe_subscription_id, 'sub_1')

    def test_max_lookup_keys_map_to_distinct_tiers(self):
        # The two Max price points are separate plans, not one collapsed tier.
        self._post_event(
            'customer.subscription.created',
            self._subscription(lookup_key='max_10x_monthly'),
        )
        self.assertEqual(self.user.subscription.plan, 'max_10x')

    def test_lookup_key_that_is_a_plan_id_resolves(self):
        # Backward-compatible fallback: a lookup_key equal to a plan id works.
        self._post_event(
            'customer.subscription.created', self._subscription(lookup_key='pro')
        )
        self.assertEqual(self.user.subscription.plan, 'pro')

    def test_updated_event_changes_plan(self):
        Subscription.objects.create(user=self.user, plan='pro')
        self._post_event(
            'customer.subscription.updated',
            self._subscription(lookup_key='max_5x_monthly'),
        )
        self.user.subscription.refresh_from_db()
        self.assertEqual(self.user.subscription.plan, 'max_5x')

    def test_metadata_plan_is_the_fallback(self):
        self._post_event(
            'customer.subscription.created',
            self._subscription(metadata={'plan': 'max_5x'}),
        )
        self.assertEqual(self.user.subscription.plan, 'max_5x')

    def test_unknown_plan_leaves_subscription_unchanged(self):
        Subscription.objects.create(user=self.user, plan='pro')
        self._post_event(
            'customer.subscription.updated',
            self._subscription(lookup_key='mystery-price'),
        )
        self.user.subscription.refresh_from_db()
        self.assertEqual(self.user.subscription.plan, 'pro')

    def test_deleted_event_downgrades_to_free(self):
        Subscription.objects.create(
            user=self.user, plan='max_5x', stripe_subscription_id='sub_1'
        )
        self._post_event(
            'customer.subscription.deleted',
            self._subscription(lookup_key='max_5x_monthly'),
        )
        self.user.subscription.refresh_from_db()
        self.assertEqual(self.user.subscription.plan, 'free')
        self.assertEqual(self.user.subscription.stripe_subscription_id, '')

    def test_unknown_customer_is_ignored(self):
        resp = self._post_event(
            'customer.subscription.created',
            self._subscription(lookup_key='pro', customer='cus_stranger'),
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertFalse(Subscription.objects.exists())

    def test_deleted_event_for_another_subscription_is_ignored(self):
        # Upgrading via checkout creates a new subscription before the old
        # one is cancelled; the old one's deleted event must not downgrade
        # the plan the user is actually paying for.
        Subscription.objects.create(
            user=self.user, plan='max_5x', stripe_subscription_id='sub_new'
        )
        self._post_event(
            'customer.subscription.deleted',
            self._subscription(lookup_key='pro_monthly', sub_id='sub_old'),
        )
        self.user.subscription.refresh_from_db()
        self.assertEqual(self.user.subscription.plan, 'max_5x')
        self.assertEqual(self.user.subscription.stripe_subscription_id, 'sub_new')

    def test_updated_event_for_another_subscription_is_ignored(self):
        # A late 'updated' for the replaced subscription (Stripe does not
        # guarantee ordering) must not overwrite the stored plan.
        Subscription.objects.create(
            user=self.user, plan='max_5x', stripe_subscription_id='sub_new'
        )
        self._post_event(
            'customer.subscription.updated',
            self._subscription(lookup_key='pro_monthly', sub_id='sub_old'),
        )
        self.user.subscription.refresh_from_db()
        self.assertEqual(self.user.subscription.plan, 'max_5x')
        self.assertEqual(self.user.subscription.stripe_subscription_id, 'sub_new')

    def test_created_event_for_new_active_subscription_takes_over(self):
        # The upgrade-checkout path: a freshly-created, in-good-standing
        # subscription becomes the stored one.
        Subscription.objects.create(
            user=self.user, plan='pro', stripe_subscription_id='sub_old'
        )
        # Replacing sub_old cancels it; keep that lookup off the network.
        with patch('apps.Payments.api.views.stripe.Subscription.retrieve',
                   return_value={'id': 'sub_old', 'status': 'canceled'}):
            self._post_event(
                'customer.subscription.created',
                self._subscription(lookup_key='max_5x_monthly', sub_id='sub_new'),
            )
        self.user.subscription.refresh_from_db()
        self.assertEqual(self.user.subscription.plan, 'max_5x')
        self.assertEqual(self.user.subscription.stripe_subscription_id, 'sub_new')

    def test_created_event_for_incomplete_subscription_does_not_take_over(self):
        Subscription.objects.create(
            user=self.user, plan='pro', stripe_subscription_id='sub_old'
        )
        self._post_event(
            'customer.subscription.created',
            self._subscription(lookup_key='max_5x_monthly', sub_id='sub_new', sub_status='incomplete'),
        )
        self.user.subscription.refresh_from_db()
        self.assertEqual(self.user.subscription.plan, 'pro')
        self.assertEqual(self.user.subscription.stripe_subscription_id, 'sub_old')

    def test_unpaid_status_downgrades_to_free(self):
        # Dunning exhausted with the 'mark unpaid' setting: no deleted event
        # ever fires, so the updated event must revoke the paid plan.
        Subscription.objects.create(
            user=self.user, plan='pro', stripe_subscription_id='sub_1'
        )
        self._post_event(
            'customer.subscription.updated',
            self._subscription(lookup_key='pro', sub_status='unpaid'),
        )
        self.user.subscription.refresh_from_db()
        self.assertEqual(self.user.subscription.plan, 'free')
        # The id stays so later events for this subscription still match.
        self.assertEqual(self.user.subscription.stripe_subscription_id, 'sub_1')

    def test_past_due_status_leaves_plan_unchanged(self):
        # Stripe is still retrying the charge — entitlement holds meanwhile.
        Subscription.objects.create(
            user=self.user, plan='pro', stripe_subscription_id='sub_1'
        )
        self._post_event(
            'customer.subscription.updated',
            self._subscription(lookup_key='pro', sub_status='past_due'),
        )
        self.user.subscription.refresh_from_db()
        self.assertEqual(self.user.subscription.plan, 'pro')

    def test_missing_status_is_treated_as_healthy(self):
        # Defensive: real Stripe events always carry a status, but its
        # absence must not strip entitlement.
        subscription = self._subscription(lookup_key='pro')
        del subscription['status']
        self._post_event('customer.subscription.created', subscription)
        self.assertEqual(self.user.subscription.plan, 'pro')


# --------------------------------------------------------------------------- #
# API endpoints
# --------------------------------------------------------------------------- #
class ReplacedSubscriptionTests(APITestCase):
    """A second subscription that completes cancels the one it replaced."""

    def setUp(self):
        self.user = make_user()
        StripeCustomer.objects.create(user=self.user, stripe_customer_id='cus_42')
        Subscription.objects.create(user=self.user, plan='pro', stripe_subscription_id='sub_old')
        self.url = reverse('api-stripe-webhook')

    def _post_created(self, sub_id, old_status='active'):
        event = SimpleNamespace(
            type='customer.subscription.created',
            data=SimpleNamespace(object={
                'id': sub_id,
                'customer': 'cus_42',
                'status': 'active',
                'items': {'data': [{'price': {'lookup_key': 'max_5x_monthly'}}]},
                'metadata': {},
            }),
        )
        with override_settings(STRIPE_WEBHOOK_SECRET='whsec_test'), \
                patch('apps.Payments.api.views.stripe_service') as mock_service, \
                patch('apps.Payments.api.views.stripe.Subscription.retrieve') as mock_retrieve:
            mock_service.verify_webhook_event.return_value = event
            mock_retrieve.return_value = {'id': 'sub_old', 'status': old_status}
            resp = self.client.post(self.url, {}, HTTP_STRIPE_SIGNATURE='sig')
        return resp, mock_service, mock_retrieve

    def test_new_subscription_cancels_the_replaced_one(self):
        resp, mock_service, _ = self._post_created('sub_new')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.user.subscription.refresh_from_db()
        self.assertEqual(self.user.subscription.plan, 'max_5x')
        self.assertEqual(self.user.subscription.stripe_subscription_id, 'sub_new')
        mock_service.cancel_subscription.assert_called_once_with('sub_old')

    def test_an_already_ended_subscription_is_left_alone(self):
        _, mock_service, _ = self._post_created('sub_new', old_status='canceled')
        mock_service.cancel_subscription.assert_not_called()

    def test_an_update_to_the_same_subscription_cancels_nothing(self):
        _, mock_service, mock_retrieve = self._post_created('sub_old')
        mock_service.cancel_subscription.assert_not_called()
        mock_retrieve.assert_not_called()

    def test_a_failed_cancel_still_grants_the_new_plan(self):
        event = SimpleNamespace(
            type='customer.subscription.created',
            data=SimpleNamespace(object={
                'id': 'sub_new', 'customer': 'cus_42', 'status': 'active',
                'items': {'data': [{'price': {'lookup_key': 'max_5x_monthly'}}]},
                'metadata': {},
            }),
        )
        with override_settings(STRIPE_WEBHOOK_SECRET='whsec_test'), \
                patch('apps.Payments.api.views.stripe_service') as mock_service, \
                patch('apps.Payments.api.views.stripe.Subscription.retrieve',
                      side_effect=Exception('stripe down')):
            mock_service.verify_webhook_event.return_value = event
            resp = self.client.post(self.url, {}, HTTP_STRIPE_SIGNATURE='sig')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.user.subscription.refresh_from_db()
        self.assertEqual(self.user.subscription.plan, 'max_5x')


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
        # The registry rides along so the frontend can render plan options.
        self.assertEqual(
            [p['id'] for p in resp.data['plans']],
            ['free', 'pro', 'max_5x', 'max_10x'],
        )
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


class CheckoutSessionTests(APITestCase):
    def setUp(self):
        self.user = make_user()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.url = reverse('api-create-checkout-session')

    @patch('apps.Payments.api.views.stripe.Price.list')
    @patch('apps.Payments.api.views.stripe_service')
    def test_subscription_checkout_uses_lookup_key(self, mock_stripe, mock_prices):
        mock_prices.return_value = SimpleNamespace(
            data=[SimpleNamespace(id='price_pro')]
        )
        mock_stripe.create_customer.return_value = MagicMock(id='cus_new')
        session = MagicMock()
        session.id = 'cs_1'
        session.url = 'https://checkout.stripe.test/cs_1'
        mock_stripe.create_checkout_session.return_value = session

        resp = self.client.post(self.url, {'lookup_key': 'pro_monthly'})

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['session_id'], 'cs_1')
        kwargs = mock_stripe.create_checkout_session.call_args.kwargs
        self.assertEqual(kwargs['mode'], 'subscription')
        self.assertEqual(kwargs['customer'], 'cus_new')

    @patch('apps.Payments.api.views.stripe.Price.list')
    @patch('apps.Payments.api.views.stripe_service')
    def test_existing_subscriber_cannot_start_a_second_subscription(self, mock_stripe, mock_prices):
        # A second checkout would bill them twice; plan changes go through
        # change_plan on the subscription they already have.
        StripeCustomer.objects.create(user=self.user, stripe_customer_id='cus_1')
        mock_stripe.list_live_subscriptions.return_value = [{'id': 'sub_1', 'status': 'active'}]

        resp = self.client.post(self.url, {'lookup_key': 'max_5x_monthly'})

        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(resp.data['code'], 'subscription_exists')
        mock_stripe.create_checkout_session.assert_not_called()
        mock_prices.assert_not_called()

    def test_lookup_key_is_required(self):
        # There is no one-time purchase mode any more, so an amount alone is
        # not a valid checkout.
        resp = self.client.post(self.url, {'amount': 20})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unknown_lookup_key_is_refused(self):
        # Selling a price the webhook can't resolve would take money without
        # granting a plan.
        resp = self.client.post(self.url, {'lookup_key': 'mystery_monthly'})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class ChangePlanTests(APITestCase):
    """Plan changes swap the price on the existing subscription."""

    def setUp(self):
        self.user = make_user()
        self.client.force_authenticate(user=self.user)
        StripeCustomer.objects.create(user=self.user, stripe_customer_id='cus_1')
        Subscription.objects.create(user=self.user, plan='pro', stripe_subscription_id='sub_1')
        self.url = reverse('api-change-plan')
        self.live = {
            'id': 'sub_1',
            'status': 'active',
            'items': {'data': [{'id': 'si_1', 'price': {'id': 'price_pro'}}]},
        }

    def _post(self, lookup_key='max_5x_monthly', live=None, updated=None, price_id='price_max5'):
        with patch('apps.Payments.api.views.stripe_service') as mock_service, \
                patch('apps.Payments.api.views.stripe.Price.list') as mock_prices:
            mock_service.list_live_subscriptions.return_value = [self.live] if live is None else live
            mock_service.change_subscription_price.return_value = (
                updated if updated is not None else {'id': 'sub_1', 'pending_update': None}
            )
            mock_prices.return_value = SimpleNamespace(data=[SimpleNamespace(id=price_id)])
            resp = self.client.post(self.url, {'lookup_key': lookup_key}, format='json')
        return resp, mock_service

    def test_upgrade_changes_the_existing_subscription(self):
        resp, mock_service = self._post()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_service.change_subscription_price.assert_called_once_with(self.live, 'price_max5')
        mock_service.create_checkout_session.assert_not_called()
        self.user.subscription.refresh_from_db()
        self.assertEqual(self.user.subscription.plan, 'max_5x')
        self.assertEqual(self.user.subscription.stripe_subscription_id, 'sub_1')

    def test_a_pending_update_grants_nothing(self):
        # pending_if_incomplete: the proration invoice wasn't paid, so the
        # old price is still in force.
        resp, _ = self._post(updated={'id': 'sub_1', 'pending_update': {'expires_at': 1}})
        self.assertEqual(resp.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.user.subscription.refresh_from_db()
        self.assertEqual(self.user.subscription.plan, 'pro')

    def test_without_a_subscription_there_is_nothing_to_change(self):
        resp, mock_service = self._post(live=[])
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data['code'], 'no_subscription')
        mock_service.change_subscription_price.assert_not_called()

    def test_past_due_must_fix_payment_first(self):
        resp, mock_service = self._post(live=[dict(self.live, status='past_due')])
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)
        mock_service.change_subscription_price.assert_not_called()

    def test_same_plan_is_refused(self):
        resp, mock_service = self._post(lookup_key='pro_monthly', price_id='price_pro')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data['code'], 'same_plan')
        mock_service.change_subscription_price.assert_not_called()

    def test_free_is_not_a_plan_change(self):
        # Going to Free is a cancellation, handled in the billing portal.
        resp, _ = self._post(lookup_key='free_monthly')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class RedirectUrlAllowlistTests(APITestCase):
    """Caller-supplied Stripe redirect targets are confined to this app's origin."""

    def setUp(self):
        self.user = make_user()
        self.client.force_authenticate(user=self.user)
        self.url = reverse('api-create-checkout-session')

    @override_settings(FRONTEND_URL='https://app.imagi.test')
    def test_foreign_origin_is_rejected(self):
        # The resulting checkout.stripe.com page carries Imagi's real merchant
        # branding, so its redirect must not be attacker-chosen.
        resp = self.client.post(self.url, {
            'lookup_key': 'pro_monthly',
            'cancel_url': 'https://imagi-billing.example/signin',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('not allowed', resp.data['error'])

    @override_settings(FRONTEND_URL='https://app.imagi.test')
    def test_protocol_relative_url_is_rejected(self):
        resp = self.client.post(self.url, {
            'lookup_key': 'pro_monthly',
            'success_url': '//evil.example/receipt',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(FRONTEND_URL='https://app.imagi.test')
    @patch('apps.Payments.api.views.stripe_service')
    @patch('apps.Payments.api.views.stripe')
    @patch('apps.Payments.api.views._ensure_stripe_customer', return_value='cus_1')
    def test_same_origin_url_is_accepted(self, _cust, mock_stripe, mock_service):
        mock_stripe.Price.list.return_value = SimpleNamespace(
            data=[SimpleNamespace(id='price_1')]
        )
        mock_service.create_checkout_session.return_value = SimpleNamespace(
            id='cs_1', url='https://checkout.stripe.com/c/pay/cs_1'
        )
        resp = self.client.post(self.url, {
            'lookup_key': 'pro_monthly',
            'cancel_url': 'https://app.imagi.test/payments/cancel',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    @override_settings(FRONTEND_URL='https://app.imagi.test')
    @patch('apps.Payments.api.views.stripe_service')
    @patch('apps.Payments.api.views.stripe')
    @patch('apps.Payments.api.views._ensure_stripe_customer', return_value='cus_1')
    def test_relative_path_is_resolved_against_frontend_url(self, _cust, mock_stripe, mock_service):
        mock_stripe.Price.list.return_value = SimpleNamespace(
            data=[SimpleNamespace(id='price_1')]
        )
        mock_service.create_checkout_session.return_value = SimpleNamespace(
            id='cs_1', url='https://checkout.stripe.com/c/pay/cs_1'
        )
        resp = self.client.post(self.url, {
            'lookup_key': 'pro_monthly',
            'cancel_url': '/payments/goodbye',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        kwargs = mock_service.create_checkout_session.call_args.kwargs
        self.assertEqual(kwargs['cancel_url'], 'https://app.imagi.test/payments/goodbye')


# --------------------------------------------------------------------------- #
# Real Stripe objects (not dicts)
# --------------------------------------------------------------------------- #
def _stripe_object(data):
    """What the Stripe library actually hands back: a StripeObject, not a dict."""
    import stripe
    return stripe.StripeObject.construct_from(data, 'sk_test_x')


def _subscription_payload(sub_id='sub_1', lookup_key='pro_monthly', sub_status='active'):
    return {
        'id': sub_id,
        'object': 'subscription',
        'customer': 'cus_42',
        'status': sub_status,
        'created': 1,
        'items': {
            'object': 'list',
            'data': [{'id': 'si_1', 'price': {'id': 'price_1', 'lookup_key': lookup_key}}],
        },
        'metadata': {},
    }


class RealStripeObjectTests(APITestCase):
    """The mocked tests above pass dicts; Stripe passes StripeObjects.

    stripe-python 13+ StripeObjects have no .get(), so every path that reads a
    subscription is exercised here with the real type.
    """

    def setUp(self):
        self.user = make_user()
        StripeCustomer.objects.create(user=self.user, stripe_customer_id='cus_42')

    def _signed_post(self, payload, secret='whsec_test'):
        import hashlib
        import hmac
        import json
        import time
        body = json.dumps(payload)
        ts = int(time.time())
        sig = hmac.new(secret.encode(), f'{ts}.{body}'.encode(), hashlib.sha256).hexdigest()
        with override_settings(STRIPE_WEBHOOK_SECRET=secret):
            return self.client.post(
                reverse('api-stripe-webhook'), body, content_type='application/json',
                HTTP_STRIPE_SIGNATURE=f't={ts},v1={sig}',
            )

    def test_a_genuinely_signed_event_grants_the_plan(self):
        # End to end through stripe.Webhook.construct_event, which yields a
        # StripeObject — the shape a real Stripe delivery has.
        resp = self._signed_post({
            'id': 'evt_1',
            'object': 'event',
            'type': 'customer.subscription.created',
            'data': {'object': _subscription_payload(lookup_key='max_10x_monthly')},
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.user.subscription.refresh_from_db()
        self.assertEqual(self.user.subscription.plan, 'max_10x')
        self.assertEqual(self.user.subscription.stripe_subscription_id, 'sub_1')

    def test_a_failed_sync_is_not_acked(self):
        # A 200 would tell Stripe to stop retrying an event that was never
        # applied, so the customer pays while the plan never changes.
        with patch('apps.Payments.api.views.Subscription.objects.update_or_create',
                   side_effect=RuntimeError('db down')):
            resp = self._signed_post({
                'id': 'evt_2',
                'object': 'event',
                'type': 'customer.subscription.created',
                'data': {'object': _subscription_payload()},
            })
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_list_live_subscriptions_reads_stripe_objects(self):
        from apps.Payments.services.stripe_service import StripeService
        listing = SimpleNamespace(data=[
            _stripe_object(_subscription_payload('sub_old', sub_status='canceled')),
            _stripe_object(_subscription_payload('sub_live')),
        ])
        with patch('apps.Payments.services.stripe_service.stripe.Subscription.list',
                   return_value=listing):
            live = StripeService().list_live_subscriptions('cus_42')
        self.assertEqual([s['id'] for s in live], ['sub_live'])
        self.assertIsInstance(live[0], dict)

    def test_change_plan_with_stripe_objects(self):
        self.client.force_authenticate(user=self.user)
        Subscription.objects.create(user=self.user, plan='pro', stripe_subscription_id='sub_1')
        updated = _stripe_object(dict(
            _subscription_payload(lookup_key='max_5x_monthly'), pending_update=None,
        ))
        with patch('apps.Payments.services.stripe_service.stripe.Subscription.list',
                   return_value=SimpleNamespace(data=[_stripe_object(_subscription_payload())])), \
                patch('apps.Payments.services.stripe_service.stripe.Subscription.modify',
                      return_value=updated) as mock_modify, \
                patch('apps.Payments.api.views.stripe.Price.list',
                      return_value=SimpleNamespace(data=[SimpleNamespace(id='price_max5')])):
            resp = self.client.post(
                reverse('api-change-plan'), {'lookup_key': 'max_5x_monthly'}, format='json'
            )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(mock_modify.call_args.kwargs['items'], [{'id': 'si_1', 'price': 'price_max5'}])
        self.user.subscription.refresh_from_db()
        self.assertEqual(self.user.subscription.plan, 'max_5x')

    def test_session_status_reads_a_stripe_object(self):
        self.client.force_authenticate(user=self.user)
        session = _stripe_object({
            'id': 'cs_1', 'object': 'checkout.session', 'payment_status': 'paid',
            'mode': 'subscription', 'metadata': {'user_id': str(self.user.id)},
        })
        with patch('apps.Payments.api.views.stripe_service') as mock_service:
            mock_service.get_session_status.return_value = session
            resp = self.client.get(reverse('api-session-status'), {'session_id': 'cs_1'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['status'], 'complete')

    @patch('apps.Payments.api.views.stripe.Price.list')
    @patch('apps.Payments.api.views.stripe_service')
    def test_checkout_tags_the_subscription_with_its_user(self, mock_service, mock_prices):
        self.client.force_authenticate(user=self.user)
        mock_service.list_live_subscriptions.return_value = []
        mock_prices.return_value = SimpleNamespace(data=[SimpleNamespace(id='price_pro')])
        mock_service.create_checkout_session.return_value = MagicMock(id='cs_1', url='https://x')
        with patch('apps.Payments.api.views.payment_method_service.get_stripe_customer_id',
                   return_value='cus_42'):
            self.client.post(reverse('api-create-checkout-session'), {'lookup_key': 'pro_monthly'})
        self.assertEqual(
            mock_service.create_checkout_session.call_args.kwargs['subscription_metadata'],
            {'user_id': str(self.user.id)},
        )
