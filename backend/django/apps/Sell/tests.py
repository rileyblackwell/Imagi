"""
Tests for the Sell app: credential handling, catalog management, checkout
session creation (with Stripe mocked), webhook processing with real
signatures, and order lifecycle.
"""

import hashlib
import hmac
import json
import time
from unittest.mock import patch

import stripe as stripe_sdk
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase

from apps.Products.Imagi.ProjectManager.models import Project

from .models import (
    Customer,
    Order,
    OrderItem,
    Product,
    SellSettings,
    decrypt_secret,
    encrypt_secret,
)
from .services.stripe_client import StripeClientError

User = get_user_model()

TEST_SECRET_KEY = 'sk_test_' + 'a' * 24
TEST_PUBLISHABLE_KEY = 'pk_test_' + 'b' * 24
TEST_WEBHOOK_SECRET = 'whsec_' + 'c' * 32


def stripe_signature(secret: str, payload: bytes) -> str:
    """Compute a Stripe-Signature header the way Stripe does."""
    timestamp = int(time.time())
    signed_payload = f'{timestamp}.'.encode() + payload
    digest = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()
    return f't={timestamp},v1={digest}'


class SellAPITestCase(APITestCase):
    """Shared fixtures: a user, their project, and an authenticated client."""

    def setUp(self):
        self.user = User.objects.create_user(username='owner', password='pass12345')
        self.other_user = User.objects.create_user(username='intruder', password='pass12345')
        self.project = Project.objects.create(name='Bloom Coffee', user=self.user)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.base = f'/api/v1/sell/projects/{self.project.id}'

    def configure_stripe(self, **overrides):
        settings_obj, _ = SellSettings.objects.get_or_create(project=self.project)
        settings_obj.stripe_publishable_key = overrides.get(
            'publishable_key', TEST_PUBLISHABLE_KEY
        )
        settings_obj.stripe_secret_key = overrides.get('secret_key', TEST_SECRET_KEY)
        settings_obj.stripe_webhook_secret = overrides.get('webhook_secret', '')
        settings_obj.currency = overrides.get('currency', 'usd')
        settings_obj.save()
        return settings_obj

    def add_product(self, name='Latte', price_cents=500, is_active=True):
        return Product.objects.create(
            project=self.project,
            name=name,
            price_cents=price_cents,
            is_active=is_active,
        )

    def make_session_payload(self, order, **overrides):
        """A checkout.session object dict the way Stripe sends it."""
        session = {
            'id': order.stripe_checkout_session_id or 'cs_test_1',
            'object': 'checkout.session',
            'status': 'complete',
            'payment_status': 'paid',
            'payment_intent': 'pi_test_1',
            'amount_total': order.amount_total_cents,
            'customer_details': {'email': 'ada@example.com', 'name': 'Ada Lovelace'},
            'metadata': {
                'imagi_project_id': str(self.project.id),
                'imagi_order_id': str(order.id),
            },
        }
        session.update(overrides)
        return session


class SecretEncryptionTests(APITestCase):
    def test_round_trip(self):
        token = encrypt_secret('sk_test_supersecret')
        self.assertNotEqual(token, 'sk_test_supersecret')
        self.assertNotIn('supersecret', token)
        self.assertEqual(decrypt_secret(token), 'sk_test_supersecret')

    def test_empty_and_garbage(self):
        self.assertEqual(encrypt_secret(''), '')
        self.assertEqual(decrypt_secret(''), '')
        self.assertEqual(decrypt_secret('not-a-fernet-token'), '')


class SellSettingsAPITests(SellAPITestCase):
    def test_get_creates_default_settings(self):
        response = self.client.get(f'{self.base}/settings/')
        self.assertEqual(response.status_code, 200)
        data = response.json()['settings']
        self.assertFalse(data['is_configured'])
        self.assertFalse(data['stripe_secret_key_set'])
        self.assertNotIn('stripe_secret_key', data)
        self.assertNotIn('stripe_webhook_secret', data)

    def test_update_stores_encrypted_secrets_and_masks_them(self):
        response = self.client.put(f'{self.base}/settings/', {
            'stripe_publishable_key': TEST_PUBLISHABLE_KEY,
            'stripe_secret_key': TEST_SECRET_KEY,
            'stripe_webhook_secret': TEST_WEBHOOK_SECRET,
            'currency': 'eur',
        }, format='json')
        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()['settings']
        self.assertTrue(data['is_configured'])
        self.assertTrue(data['stripe_secret_key_set'])
        self.assertTrue(data['stripe_webhook_secret_set'])
        self.assertEqual(data['currency'], 'eur')
        self.assertNotIn('stripe_secret_key', data)

        stored = SellSettings.objects.get(project=self.project)
        self.assertNotIn(TEST_SECRET_KEY, stored.stripe_secret_key_encrypted)
        self.assertEqual(stored.stripe_secret_key, TEST_SECRET_KEY)
        self.assertEqual(stored.stripe_webhook_secret, TEST_WEBHOOK_SECRET)

    def test_blank_secret_keeps_existing_key(self):
        self.configure_stripe()
        response = self.client.put(f'{self.base}/settings/', {
            'stripe_secret_key': '',
            'currency': 'gbp',
        }, format='json')
        self.assertEqual(response.status_code, 200)
        stored = SellSettings.objects.get(project=self.project)
        self.assertEqual(stored.stripe_secret_key, TEST_SECRET_KEY)
        self.assertEqual(stored.currency, 'gbp')

    def test_clearing_publishable_key_wipes_secrets(self):
        self.configure_stripe(webhook_secret=TEST_WEBHOOK_SECRET)
        response = self.client.put(
            f'{self.base}/settings/', {'stripe_publishable_key': ''}, format='json'
        )
        self.assertEqual(response.status_code, 200)
        stored = SellSettings.objects.get(project=self.project)
        self.assertEqual(stored.stripe_secret_key_encrypted, '')
        self.assertEqual(stored.stripe_webhook_secret_encrypted, '')

    def test_rejects_malformed_keys(self):
        for payload in (
            {'stripe_secret_key': 'not-a-key'},
            {'stripe_publishable_key': 'sk_test_wrongkind'},
            {'stripe_webhook_secret': 'nope'},
        ):
            response = self.client.put(f'{self.base}/settings/', payload, format='json')
            self.assertEqual(response.status_code, 400, payload)

    def test_other_users_project_is_not_found(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(f'{self.base}/settings/')
        self.assertEqual(response.status_code, 404)

    def test_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(f'{self.base}/settings/')
        self.assertIn(response.status_code, (401, 403))


@patch('apps.Sell.services.sell_service.StripeClient')
class VerifyConnectionTests(SellAPITestCase):
    def test_verify_caches_account_identity(self, MockClient):
        self.configure_stripe()
        MockClient.return_value.fetch_account.return_value = {
            'id': 'acct_1',
            'email': 'owner@bloom.coffee',
            'charges_enabled': True,
            'settings': {'dashboard': {'display_name': 'Bloom Coffee'}},
            'business_profile': {'name': ''},
        }
        response = self.client.post(f'{self.base}/settings/verify/')
        self.assertEqual(response.status_code, 200, response.content)
        payload = response.json()
        self.assertTrue(payload['verified'])
        self.assertEqual(payload['account_name'], 'Bloom Coffee')
        stored = SellSettings.objects.get(project=self.project)
        self.assertEqual(stored.account_name, 'Bloom Coffee')
        self.assertIsNotNone(stored.last_verified_at)
        MockClient.assert_called_once_with(TEST_SECRET_KEY)

    def test_verify_requires_configuration(self, MockClient):
        response = self.client.post(f'{self.base}/settings/verify/')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Stripe is not connected', response.json()['error'])

    def test_verify_surfaces_stripe_rejection(self, MockClient):
        self.configure_stripe()
        MockClient.return_value.fetch_account.side_effect = StripeClientError('Invalid API Key')
        response = self.client.post(f'{self.base}/settings/verify/')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid API Key', response.json()['error'])


class ProductAPITests(SellAPITestCase):
    def test_create_list_update_delete(self):
        response = self.client.post(f'{self.base}/products/', {
            'name': 'Latte',
            'description': 'Our house latte',
            'price_cents': 500,
        }, format='json')
        self.assertEqual(response.status_code, 201, response.content)
        product = response.json()['product']
        self.assertTrue(product['is_active'])

        response = self.client.get(f'{self.base}/products/', {'search': 'latte'})
        self.assertEqual(response.json()['total'], 1)

        product_id = product['id']
        response = self.client.patch(
            f'{self.base}/products/{product_id}/', {'is_active': False}, format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['product']['is_active'])

        response = self.client.get(f'{self.base}/products/', {'active': 'true'})
        self.assertEqual(response.json()['total'], 0)

        response = self.client.delete(f'{self.base}/products/{product_id}/')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.project.sell_products.count(), 0)

    def test_rejects_price_below_stripe_minimum(self):
        response = self.client.post(f'{self.base}/products/', {
            'name': 'Sticker',
            'price_cents': 25,
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_deleting_product_keeps_order_history(self):
        product = self.add_product()
        order = Order.objects.create(project=self.project, amount_total_cents=500)
        OrderItem.objects.create(
            order=order, product=product, product_name=product.name,
            unit_price_cents=500, quantity=1,
        )
        self.client.delete(f'{self.base}/products/{product.id}/')
        item = order.items.get()
        self.assertIsNone(item.product)
        self.assertEqual(item.product_name, 'Latte')

    def test_storefront_lists_active_products_without_auth(self):
        self.add_product('Latte', 500)
        self.add_product('Retired blend', 700, is_active=False)
        public_client = APIClient()  # unauthenticated, like a customer
        response = public_client.get(f'/api/v1/sell/storefront/{self.project.id}/products/')
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload['products']), 1)
        self.assertEqual(payload['products'][0]['name'], 'Latte')
        self.assertEqual(payload['currency'], 'usd')


@patch('apps.Sell.services.stripe_client.stripe')
class CheckoutTests(SellAPITestCase):
    def setUp(self):
        super().setUp()
        self.configure_stripe()
        self.public_client = APIClient()
        self.checkout_url = f'/api/v1/sell/storefront/{self.project.id}/checkout/'

    def mock_session(self, MockStripe, session_id='cs_test_1'):
        MockStripe.error = stripe_sdk.error  # keep real exception classes
        MockStripe.checkout.Session.create.return_value = {
            'id': session_id,
            'url': f'https://checkout.stripe.com/c/pay/{session_id}',
        }
        return MockStripe.checkout.Session.create

    def test_checkout_creates_pending_order_with_catalog_prices(self, MockStripe):
        create = self.mock_session(MockStripe)
        latte = self.add_product('Latte', 500)
        beans = self.add_product('Beans', 1500)

        response = self.public_client.post(self.checkout_url, {
            'items': [
                {'product_id': latte.id, 'quantity': 2},
                {'product_id': beans.id, 'quantity': 1, 'price_cents': 1},  # ignored
            ],
            'customer_email': 'ada@example.com',
        }, format='json')
        self.assertEqual(response.status_code, 201, response.content)
        payload = response.json()
        self.assertEqual(payload['session_id'], 'cs_test_1')
        self.assertIn('checkout.stripe.com', payload['checkout_url'])

        order = self.project.sell_orders.get()
        self.assertEqual(order.status, Order.STATUS_PENDING)
        self.assertEqual(order.amount_total_cents, 2 * 500 + 1500)
        self.assertEqual(order.stripe_checkout_session_id, 'cs_test_1')
        self.assertEqual(order.items.count(), 2)

        # The session is created with the project's own key and catalog prices.
        _, kwargs = create.call_args
        self.assertEqual(kwargs['api_key'], TEST_SECRET_KEY)
        amounts = {
            item['price_data']['unit_amount'] for item in kwargs['line_items']
        }
        self.assertEqual(amounts, {500, 1500})
        self.assertEqual(kwargs['metadata']['imagi_order_id'], str(order.id))
        self.assertEqual(kwargs['customer_email'], 'ada@example.com')

    def test_checkout_rejects_bad_carts(self, MockStripe):
        self.mock_session(MockStripe)
        latte = self.add_product('Latte', 500)
        inactive = self.add_product('Retired', 700, is_active=False)

        for items in (
            None,
            [],
            [{'product_id': inactive.id}],
            [{'product_id': 999999}],
            [{'product_id': latte.id, 'quantity': 0}],
            [{'product_id': latte.id, 'quantity': 101}],
        ):
            response = self.public_client.post(
                self.checkout_url, {'items': items}, format='json'
            )
            self.assertEqual(response.status_code, 400, items)
        self.assertEqual(self.project.sell_orders.count(), 0)

    def test_checkout_rejects_relative_redirect_urls(self, MockStripe):
        self.mock_session(MockStripe)
        latte = self.add_product()
        response = self.public_client.post(self.checkout_url, {
            'items': [{'product_id': latte.id}],
            'success_url': 'javascript:alert(1)',
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_checkout_requires_stripe_configuration(self, MockStripe):
        SellSettings.objects.filter(project=self.project).delete()
        latte = self.add_product()
        response = self.public_client.post(
            self.checkout_url, {'items': [{'product_id': latte.id}]}, format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('Stripe is not connected', response.json()['error'])

    def test_stripe_failure_leaves_no_orphan_order(self, MockStripe):
        MockStripe.error = stripe_sdk.error
        MockStripe.checkout.Session.create.side_effect = stripe_sdk.error.StripeError(
            'Your account cannot currently make charges.'
        )
        latte = self.add_product()
        response = self.public_client.post(
            self.checkout_url, {'items': [{'product_id': latte.id}]}, format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.project.sell_orders.count(), 0)

    def test_payment_link_endpoint_for_owner(self, MockStripe):
        self.mock_session(MockStripe, session_id='cs_test_link')
        latte = self.add_product()
        response = self.client.post(
            f'{self.base}/products/{latte.id}/payment-link/', {}, format='json'
        )
        self.assertEqual(response.status_code, 201, response.content)
        payload = response.json()
        self.assertIn('cs_test_link', payload['checkout_url'])
        self.assertEqual(payload['order']['status'], 'pending')


class WebhookTests(SellAPITestCase):
    def setUp(self):
        super().setUp()
        self.configure_stripe(webhook_secret=TEST_WEBHOOK_SECRET)
        self.webhook_client = APIClient()  # unauthenticated, like Stripe
        self.path = f'/api/v1/sell/webhooks/{self.project.id}/stripe/'

    def make_order(self, **overrides):
        defaults = {
            'project': self.project,
            'status': Order.STATUS_PENDING,
            'amount_total_cents': 500,
            'stripe_checkout_session_id': 'cs_test_1',
        }
        defaults.update(overrides)
        return Order.objects.create(**defaults)

    def post_event(self, event_type, data_object, secret=TEST_WEBHOOK_SECRET):
        payload = json.dumps({
            'id': 'evt_test_1',
            'object': 'event',
            'type': event_type,
            'data': {'object': data_object},
        }).encode()
        return self.webhook_client.post(
            self.path,
            payload,
            content_type='application/json',
            headers={'Stripe-Signature': stripe_signature(secret, payload)},
        )

    def test_completed_session_marks_order_paid_and_upserts_customer(self):
        order = self.make_order()
        response = self.post_event(
            'checkout.session.completed', self.make_session_payload(order)
        )
        self.assertEqual(response.status_code, 200, response.content)

        order.refresh_from_db()
        self.assertEqual(order.status, Order.STATUS_PAID)
        self.assertIsNotNone(order.paid_at)
        self.assertEqual(order.stripe_payment_intent_id, 'pi_test_1')
        self.assertEqual(order.customer_email, 'ada@example.com')

        customer = self.project.sell_customers.get()
        self.assertEqual(customer.email, 'ada@example.com')
        self.assertEqual(customer.name, 'Ada Lovelace')
        self.assertEqual(customer.source, 'checkout')
        self.assertEqual(order.customer_id, customer.id)

        # Replays are idempotent: still one customer, order untouched.
        first_paid_at = order.paid_at
        self.post_event('checkout.session.completed', self.make_session_payload(order))
        order.refresh_from_db()
        self.assertEqual(order.paid_at, first_paid_at)
        self.assertEqual(self.project.sell_customers.count(), 1)

    def test_expired_session_cancels_pending_order(self):
        order = self.make_order()
        response = self.post_event(
            'checkout.session.expired',
            self.make_session_payload(order, status='expired', payment_status='unpaid'),
        )
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.STATUS_CANCELED)

    def test_refund_marks_paid_order_refunded(self):
        order = self.make_order(
            status=Order.STATUS_PAID, stripe_payment_intent_id='pi_test_1'
        )
        response = self.post_event('charge.refunded', {
            'id': 'ch_test_1',
            'object': 'charge',
            'payment_intent': 'pi_test_1',
        })
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.STATUS_REFUNDED)

    def test_rejects_bad_signature(self):
        order = self.make_order()
        response = self.post_event(
            'checkout.session.completed',
            self.make_session_payload(order),
            secret='whsec_' + 'x' * 32,
        )
        self.assertEqual(response.status_code, 403)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.STATUS_PENDING)

    def test_rejects_when_no_signing_secret_stored(self):
        SellSettings.objects.filter(project=self.project).update(
            stripe_webhook_secret_encrypted=''
        )
        order = self.make_order()
        response = self.post_event(
            'checkout.session.completed', self.make_session_payload(order)
        )
        self.assertEqual(response.status_code, 403)

    def test_unknown_event_type_is_ignored(self):
        response = self.post_event('customer.created', {'id': 'cus_1'})
        self.assertEqual(response.status_code, 200)


class OrderAPITests(SellAPITestCase):
    def setUp(self):
        super().setUp()
        self.configure_stripe()

    def make_order(self, **overrides):
        defaults = {
            'project': self.project,
            'status': Order.STATUS_PENDING,
            'amount_total_cents': 500,
            'stripe_checkout_session_id': 'cs_test_1',
        }
        defaults.update(overrides)
        return Order.objects.create(**defaults)

    def test_list_filters_by_status(self):
        self.make_order()
        self.make_order(status=Order.STATUS_PAID, stripe_checkout_session_id='cs_test_2')
        response = self.client.get(f'{self.base}/orders/', {'status': 'paid'})
        payload = response.json()
        self.assertEqual(payload['total'], 1)
        self.assertEqual(payload['orders'][0]['status'], 'paid')

    def test_fulfill_only_from_paid(self):
        order = self.make_order()
        response = self.client.post(f'{self.base}/orders/{order.id}/fulfill/')
        self.assertEqual(response.status_code, 400)

        order.status = Order.STATUS_PAID
        order.save()
        response = self.client.post(f'{self.base}/orders/{order.id}/fulfill/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['order']['status'], 'fulfilled')
        order.refresh_from_db()
        self.assertIsNotNone(order.fulfilled_at)

    @patch('apps.Sell.services.stripe_client.stripe')
    def test_sync_pulls_session_state(self, MockStripe):
        MockStripe.error = stripe_sdk.error
        order = self.make_order()
        MockStripe.checkout.Session.retrieve.return_value = self.make_session_payload(order)

        response = self.client.post(f'{self.base}/orders/{order.id}/sync/')
        self.assertEqual(response.status_code, 200, response.content)
        self.assertTrue(response.json()['updated'])
        order.refresh_from_db()
        self.assertEqual(order.status, Order.STATUS_PAID)
        _, kwargs = MockStripe.checkout.Session.retrieve.call_args
        self.assertEqual(kwargs['api_key'], TEST_SECRET_KEY)

    @patch('apps.Sell.services.stripe_client.stripe')
    def test_public_session_status_syncs_pending_orders(self, MockStripe):
        MockStripe.error = stripe_sdk.error
        order = self.make_order()
        MockStripe.checkout.Session.retrieve.return_value = self.make_session_payload(order)

        public_client = APIClient()
        response = public_client.get(
            f'/api/v1/sell/storefront/{self.project.id}/sessions/cs_test_1/'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'paid')

    def test_other_users_project_is_not_found(self):
        order = self.make_order()
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(f'{self.base}/orders/{order.id}/')
        self.assertEqual(response.status_code, 404)


class CustomerAPITests(SellAPITestCase):
    def test_create_list_update_delete(self):
        response = self.client.post(f'{self.base}/customers/', {
            'name': 'Ada Lovelace',
            'email': 'Ada@Example.com',
        }, format='json')
        self.assertEqual(response.status_code, 201, response.content)
        customer = response.json()['customer']
        self.assertEqual(customer['email'], 'ada@example.com')  # normalized

        response = self.client.post(f'{self.base}/customers/', {
            'email': 'ada@example.com',
        }, format='json')
        self.assertEqual(response.status_code, 400)  # duplicate per project

        response = self.client.get(f'{self.base}/customers/', {'search': 'ada'})
        self.assertEqual(response.json()['total'], 1)

        customer_id = customer['id']
        response = self.client.patch(
            f'{self.base}/customers/{customer_id}/', {'phone': '+15551234567'}, format='json'
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.delete(f'{self.base}/customers/{customer_id}/')
        self.assertEqual(response.status_code, 204)

    def test_detail_includes_order_history_and_totals(self):
        customer = Customer.objects.create(
            project=self.project, email='ada@example.com', name='Ada'
        )
        Order.objects.create(
            project=self.project, customer=customer,
            status=Order.STATUS_PAID, amount_total_cents=1500,
        )
        Order.objects.create(
            project=self.project, customer=customer,
            status=Order.STATUS_PENDING, amount_total_cents=999,
        )
        response = self.client.get(f'{self.base}/customers/{customer.id}/')
        payload = response.json()
        self.assertEqual(payload['customer']['orders_count'], 2)
        self.assertEqual(payload['customer']['total_spent_cents'], 1500)
        self.assertEqual(len(payload['orders']), 2)


class OverviewAPITests(SellAPITestCase):
    def test_overview_counts(self):
        from django.utils import timezone

        self.configure_stripe()
        self.add_product('Latte', 500)
        self.add_product('Retired', 700, is_active=False)
        Customer.objects.create(project=self.project, email='ada@example.com')
        Order.objects.create(
            project=self.project, status=Order.STATUS_PAID,
            amount_total_cents=1500, paid_at=timezone.now(),
        )
        Order.objects.create(project=self.project, amount_total_cents=500)

        response = self.client.get(f'{self.base}/overview/')
        self.assertEqual(response.status_code, 200)
        stats = response.json()['stats']
        self.assertTrue(stats['configured'])
        self.assertEqual(stats['products_total'], 2)
        self.assertEqual(stats['products_active'], 1)
        self.assertEqual(stats['customers_total'], 1)
        self.assertEqual(stats['orders_total'], 2)
        self.assertEqual(stats['orders_pending'], 1)
        self.assertEqual(stats['orders_paid_30d'], 1)
        self.assertEqual(stats['revenue_cents_30d'], 1500)
        self.assertEqual(len(response.json()['recent_orders']), 2)
