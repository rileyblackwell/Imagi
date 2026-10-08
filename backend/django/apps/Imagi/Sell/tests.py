"""
Tests for the Sell app: credential handling, catalog management, checkout
session creation (with Stripe mocked), webhook processing with real
signatures, and order lifecycle.
"""

import hashlib
import hmac
import json
import os
import shutil
import tempfile
import time
from unittest.mock import patch

import stripe as stripe_sdk
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.test import APIClient, APITestCase

from apps.Imagi.ProjectManager.models import Project

from .models import (
    Customer,
    Order,
    OrderItem,
    Product,
    SellSettings,
    decrypt_secret,
    encrypt_secret,
)
from .services.sell_service import SellService, SellServiceError
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

    def add_product(self, name='Latte', price_cents=500, is_active=True,
                    billing_interval='one_time'):
        return Product.objects.create(
            project=self.project,
            name=name,
            price_cents=price_cents,
            is_active=is_active,
            billing_interval=billing_interval,
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


@patch('apps.Imagi.Sell.services.sell_service.StripeClient')
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


@patch('apps.Imagi.Sell.services.stripe_client.stripe')
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

    def test_checkout_rejects_foreign_redirect_origin(self, MockStripe):
        # This endpoint is unauthenticated and the project id is a sequential
        # integer, so a free-form redirect let anyone mint a Checkout link on
        # the merchant's real Stripe account that drops the paying customer on
        # an attacker's page.
        self.mock_session(MockStripe)
        latte = self.add_product()
        with override_settings(FRONTEND_URL='https://app.imagi.test'):
            response = self.public_client.post(self.checkout_url, {
                'items': [{'product_id': latte.id}],
                'success_url': 'https://evil.example/receipt',
            }, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.project.sell_orders.count(), 0)

    def test_checkout_accepts_a_path_and_resolves_it_against_frontend_url(self, MockStripe):
        session = self.mock_session(MockStripe)
        latte = self.add_product()
        with override_settings(FRONTEND_URL='https://app.imagi.test'):
            response = self.public_client.post(self.checkout_url, {
                'items': [{'product_id': latte.id}],
                'success_url': '/thanks',
            }, format='json')
        self.assertEqual(response.status_code, 201)
        kwargs = session.call_args.kwargs
        self.assertEqual(kwargs['success_url'], 'https://app.imagi.test/thanks')

    def test_service_rejects_foreign_origin_even_when_called_directly(self, MockStripe):
        # Defense in depth: a future caller reaching the service directly must
        # not be able to reintroduce the open redirect.
        self.mock_session(MockStripe)
        latte = self.add_product()
        with override_settings(FRONTEND_URL='https://app.imagi.test'):
            with self.assertRaises(SellServiceError):
                SellService(self.project).create_checkout(
                    [{'product_id': latte.id}],
                    success_url='https://evil.example/receipt',
                )

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

    def test_recurring_product_switches_to_subscription_mode(self, MockStripe):
        create = self.mock_session(MockStripe)
        plan = self.add_product('Pro plan', 900, billing_interval='month')

        response = self.public_client.post(self.checkout_url, {
            'items': [{'product_id': plan.id}],
        }, format='json')
        self.assertEqual(response.status_code, 201, response.content)

        _, kwargs = create.call_args
        self.assertEqual(kwargs['mode'], 'subscription')
        self.assertEqual(
            kwargs['line_items'][0]['price_data']['recurring'],
            {'interval': 'month'},
        )

    def test_one_time_cart_stays_in_payment_mode(self, MockStripe):
        create = self.mock_session(MockStripe)
        latte = self.add_product('Latte', 500)

        response = self.public_client.post(self.checkout_url, {
            'items': [{'product_id': latte.id}],
        }, format='json')
        self.assertEqual(response.status_code, 201)

        _, kwargs = create.call_args
        self.assertEqual(kwargs['mode'], 'payment')
        self.assertNotIn('recurring', kwargs['line_items'][0]['price_data'])

    def test_mixed_cart_uses_subscription_mode(self, MockStripe):
        # Stripe allows one-time items alongside a subscription, but not
        # recurring prices in payment mode.
        create = self.mock_session(MockStripe)
        latte = self.add_product('Latte', 500)
        plan = self.add_product('Pro plan', 900, billing_interval='month')

        response = self.public_client.post(self.checkout_url, {
            'items': [{'product_id': latte.id}, {'product_id': plan.id}],
        }, format='json')
        self.assertEqual(response.status_code, 201)

        _, kwargs = create.call_args
        self.assertEqual(kwargs['mode'], 'subscription')

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

    def test_full_refund_marks_paid_order_refunded(self):
        order = self.make_order(
            status=Order.STATUS_PAID, stripe_payment_intent_id='pi_test_1'
        )
        response = self.post_event('charge.refunded', {
            'id': 'ch_test_1',
            'object': 'charge',
            'payment_intent': 'pi_test_1',
            'refunded': True,
            'amount_refunded': 500,
        })
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.STATUS_REFUNDED)

    def test_partial_refund_keeps_order_paid(self):
        # Stripe fires charge.refunded for partial refunds too, with
        # refunded=false; the order must keep counting toward revenue.
        order = self.make_order(
            status=Order.STATUS_PAID, stripe_payment_intent_id='pi_test_1'
        )
        response = self.post_event('charge.refunded', {
            'id': 'ch_test_1',
            'object': 'charge',
            'payment_intent': 'pi_test_1',
            'refunded': False,
            'amount_refunded': 100,
        })
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.STATUS_PAID)

    def test_mixed_case_checkout_email_reuses_existing_customer(self):
        Customer.objects.create(
            project=self.project, email='ada@example.com', name='Ada Lovelace'
        )
        order = self.make_order()
        response = self.post_event(
            'checkout.session.completed',
            self.make_session_payload(
                order,
                customer_details={'email': 'Ada@Example.COM', 'name': 'Ada Lovelace'},
            ),
        )
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.customer_email, 'ada@example.com')
        self.assertEqual(self.project.sell_customers.count(), 1)
        self.assertEqual(order.customer_id, self.project.sell_customers.get().id)

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

    @patch('apps.Imagi.Sell.services.stripe_client.stripe')
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

    @patch('apps.Imagi.Sell.services.stripe_client.stripe')
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


class AppPaymentsTests(APITestCase):
    """The prebuilt payments the Sell console installs into projects."""

    def setUp(self):
        self.projects_root = tempfile.mkdtemp(prefix='imagi-test-projects-')
        self.addCleanup(shutil.rmtree, self.projects_root, ignore_errors=True)
        self.settings_override = override_settings(PROJECTS_ROOT=self.projects_root)
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)

        self.user = User.objects.create_user(username='owner', password='pass12345')
        self.project = Project.objects.create(name='Bloom Coffee', user=self.user)
        os.makedirs(self.project.project_path, exist_ok=True)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.base = f'/api/v1/sell/projects/{self.project.id}'

    def choose(self, *models):
        response = self.client.put(f'{self.base}/settings/', {'payment_models': list(models)},
                                   format='json')
        self.assertEqual(response.status_code, 200, response.content)

    def read(self, path):
        from apps.Imagi.Build.models import ProjectFile
        return ProjectFile.objects.get(project=self.project, path=path).content

    def test_state_before_install(self):
        response = self.client.get(f'{self.base}/app-payments/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['installed'])

    def test_install_requires_a_payment_model(self):
        response = self.client.post(f'{self.base}/app-payments/install/')
        self.assertEqual(response.status_code, 400)

    @patch('apps.Imagi.Sell.services.payments_restyle_service.queue_payments_restyle')
    def test_install_writes_stamped_files_for_chosen_models(self, queue):
        self.choose('subscription', 'usage')
        response = self.client.post(f'{self.base}/app-payments/install/')
        self.assertEqual(response.status_code, 201, response.content)
        payload = response.json()
        self.assertEqual(payload['routes'], ['/pricing'])
        self.assertTrue(payload['installed'])

        config = self.read('frontend/vuejs/src/apps/payments/config.ts')
        self.assertIn(f'projectId: {self.project.id}', config)
        self.assertIn('"pricing": true', config)
        self.assertIn('"store": false', config)
        self.assertNotIn('__IMAGI', config)
        # The client holds no secrets, and Stripe's placeholder survives.
        client_ts = self.read('frontend/vuejs/src/apps/payments/services/payments.ts')
        self.assertNotIn('sk_', client_ts)
        self.assertIn('session_id={CHECKOUT_SESSION_ID}', client_ts)
        backend_config = self.read('backend/django/apps/payments/config.py')
        self.assertIn(f'IMAGI_PROJECT_ID = {self.project.id}', backend_config)
        # Written to the working copy the preview runs, too.
        self.assertTrue(os.path.exists(os.path.join(
            self.project.project_path, 'frontend', 'vuejs', 'src', 'apps', 'payments',
            'views', 'PricingView.vue',
        )))
        queue.assert_called_once_with(self.project.id, self.user.id, ['/pricing'])

    @patch('apps.Imagi.Sell.services.payments_restyle_service.queue_payments_restyle')
    def test_reinstall_keeps_the_projects_look_and_flags_changes(self, queue):
        from apps.Imagi.Build.services.create_file_service import CreateFileService
        self.choose('one_time')
        self.client.post(f'{self.base}/app-payments/install/')
        css = 'frontend/vuejs/src/apps/payments/styles/payments.css'
        CreateFileService(project=self.project).create_file(
            {'name': css, 'type': 'css', 'content': '.pay-theme { --pay-bg: hotpink; }'}
        )

        self.choose('one_time', 'subscription')
        state = self.client.get(f'{self.base}/app-payments/').json()
        self.assertTrue(state['out_of_date'])

        response = self.client.post(f'{self.base}/app-payments/install/')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.read(css), '.pay-theme { --pay-bg: hotpink; }')
        self.assertFalse(response.json()['out_of_date'])
        # Only the newly added page is announced to the restyle.
        self.assertEqual(queue.call_args_list[-1].args[2], ['/pricing'])

    def test_install_requires_project_ownership(self):
        intruder = User.objects.create_user(username='intruder', password='pass12345')
        self.client.force_authenticate(user=intruder)
        response = self.client.post(f'{self.base}/app-payments/install/')
        self.assertEqual(response.status_code, 404)

    def test_agents_cannot_edit_the_payment_flow(self):
        from apps.Imagi.Build.services.protected_paths import (
            PAYMENTS_RESTYLE_PATHS,
            is_protected_path,
            refusal,
        )
        self.assertTrue(is_protected_path('frontend/vuejs/src/apps/payments/services/payments.ts'))
        self.assertTrue(is_protected_path('backend/django/apps/payments/client.py'))
        for path in PAYMENTS_RESTYLE_PATHS:
            self.assertFalse(is_protected_path(path))
        self.assertIn('prebuilt payments', refusal('frontend/vuejs/src/apps/payments/config.ts'))


class ConnectTests(SellAPITestCase):
    """Linking a project to the owner's Stripe account through Connect."""

    def setUp(self):
        super().setUp()
        self.user.email = 'owner@example.com'
        self.user.save()

    @override_settings(STRIPE_SECRET_KEY='sk_test_platform', FRONTEND_URL='http://localhost:5173')
    @patch('apps.Imagi.Sell.services.stripe_client.stripe')
    def test_start_creates_account_once_and_returns_onboarding_link(self, MockStripe):
        MockStripe.error = stripe_sdk.error
        MockStripe.Account.create.return_value = {'id': 'acct_123'}
        MockStripe.AccountLink.create.return_value = {'url': 'https://connect.stripe.com/setup/x'}

        response = self.client.post(f'{self.base}/connect/start/',
                                    {'return_path': '/imagi/project/bloom-coffee/sales'})
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()['url'], 'https://connect.stripe.com/setup/x')
        kwargs = MockStripe.Account.create.call_args.kwargs
        self.assertEqual(kwargs['api_key'], 'sk_test_platform')
        self.assertEqual(kwargs['controller']['stripe_dashboard'], {'type': 'full'})
        self.assertEqual(kwargs['email'], 'owner@example.com')
        link = MockStripe.AccountLink.create.call_args.kwargs
        self.assertEqual(link['account'], 'acct_123')
        self.assertEqual(
            link['return_url'], 'http://localhost:5173/imagi/project/bloom-coffee/sales?stripe=return'
        )

        # A second start reuses the account.
        self.client.post(f'{self.base}/connect/start/')
        self.assertEqual(MockStripe.Account.create.call_count, 1)
        self.assertEqual(SellSettings.objects.get(project=self.project).connect_account_id, 'acct_123')

    @override_settings(STRIPE_SECRET_KEY='sk_test_platform')
    @patch('apps.Imagi.Sell.services.stripe_client.stripe')
    def test_return_path_cannot_leave_imagi(self, MockStripe):
        MockStripe.error = stripe_sdk.error
        MockStripe.Account.create.return_value = {'id': 'acct_123'}
        MockStripe.AccountLink.create.return_value = {'url': 'https://connect.stripe.com/x'}
        self.client.post(f'{self.base}/connect/start/', {'return_path': 'https://evil.example/'})
        link = MockStripe.AccountLink.create.call_args.kwargs
        self.assertNotIn('evil.example', link['return_url'])

    @override_settings(STRIPE_SECRET_KEY='')
    def test_start_without_platform_key_explains(self):
        response = self.client.post(f'{self.base}/connect/start/')
        self.assertEqual(response.status_code, 400)
        self.assertIn('not available', response.json()['error'])

    @override_settings(STRIPE_SECRET_KEY='sk_test_platform')
    @patch('apps.Imagi.Sell.services.stripe_client.stripe')
    def test_refresh_caches_account_state_and_enables_checkout(self, MockStripe):
        MockStripe.error = stripe_sdk.error
        SellSettings.objects.create(project=self.project, connect_account_id='acct_123')
        MockStripe.Account.retrieve.return_value = {
            'id': 'acct_123', 'charges_enabled': True, 'payouts_enabled': False,
            'details_submitted': True, 'email': 'shop@example.com',
            'business_profile': {'name': 'Bloom Coffee LLC'},
        }
        response = self.client.post(f'{self.base}/connect/refresh/')
        self.assertEqual(response.status_code, 200, response.content)
        settings_data = response.json()['settings']
        self.assertTrue(settings_data['is_configured'])
        self.assertEqual(settings_data['connection_type'], 'connect')
        self.assertTrue(settings_data['is_test_mode'])
        self.assertEqual(settings_data['account_name'], 'Bloom Coffee LLC')
        self.assertEqual(MockStripe.Account.retrieve.call_args.args, ('acct_123',))

    def test_connected_but_unfinished_account_cannot_take_payments(self):
        SellSettings.objects.create(project=self.project, connect_account_id='acct_123')
        with override_settings(STRIPE_SECRET_KEY='sk_test_platform'):
            with self.assertRaises(SellServiceError):
                SellService(self.project)._client()

    @override_settings(STRIPE_SECRET_KEY='sk_test_platform')
    @patch('apps.Imagi.Sell.services.stripe_client.stripe')
    def test_connected_checkout_runs_on_the_connected_account(self, MockStripe):
        MockStripe.error = stripe_sdk.error
        MockStripe.checkout.Session.create.return_value = {'id': 'cs_1', 'url': 'https://x'}
        SellSettings.objects.create(
            project=self.project, connect_account_id='acct_123', connect_charges_enabled=True,
        )
        product = self.add_product()
        response = APIClient().post(
            f'/api/v1/sell/storefront/{self.project.id}/checkout/',
            {'items': [{'product_id': product.id}]}, format='json',
        )
        self.assertEqual(response.status_code, 201, response.content)
        kwargs = MockStripe.checkout.Session.create.call_args.kwargs
        self.assertEqual(kwargs['api_key'], 'sk_test_platform')
        self.assertEqual(kwargs['stripe_account'], 'acct_123')

    def test_disconnect_forgets_the_account(self):
        SellSettings.objects.create(
            project=self.project, connect_account_id='acct_123', connect_charges_enabled=True,
        )
        response = self.client.post(f'{self.base}/connect/disconnect/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['settings']['connection_type'], '')


class PaymentModelSettingsTests(SellAPITestCase):
    def test_payment_models_are_validated_and_ordered(self):
        response = self.client.put(f'{self.base}/settings/',
                                   {'payment_models': ['usage', 'one_time', 'usage']},
                                   format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['settings']['payment_models'], ['one_time', 'usage'])
        response = self.client.put(f'{self.base}/settings/', {'payment_models': ['barter']},
                                   format='json')
        self.assertEqual(response.status_code, 400)

    def test_server_key_rotation_and_reveal(self):
        response = self.client.post(f'{self.base}/server-key/')
        self.assertEqual(response.status_code, 201)
        key = response.json()['server_key']
        self.assertTrue(key.startswith('imagi_sk_'))
        self.assertTrue(response.json()['settings']['server_key_set'])
        settings_obj = SellSettings.objects.get(project=self.project)
        self.assertNotIn(key, settings_obj.server_key_encrypted)
        self.assertEqual(self.client.get(f'{self.base}/server-key/').json()['server_key'], key)

    def test_usage_product_validation(self):
        response = self.client.post(f'{self.base}/products/', {
            'name': 'Messages', 'price_cents': 1, 'billing_interval': 'usage',
        }, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('usage_unit_label', response.json())
        response = self.client.post(f'{self.base}/products/', {
            'name': 'Messages', 'price_cents': 100, 'billing_interval': 'usage',
            'usage_unit_label': 'message', 'usage_unit_count': 1000,
        }, format='json')
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(response.json()['product']['pricing_model'], 'usage')


@patch('apps.Imagi.Sell.services.stripe_client.stripe')
class UsageBillingTests(SellAPITestCase):
    """Pay as you go: metered checkout, subscriptions, usage reports."""

    def setUp(self):
        super().setUp()
        self.config = self.configure_stripe()
        self.server_key = self.config.rotate_server_key()
        self.config.save()
        self.plan = Product.objects.create(
            project=self.project, name='Messages', price_cents=100,
            billing_interval='usage', usage_unit_label='message', usage_unit_count=1000,
        )
        self.public = APIClient()
        self.storefront = f'/api/v1/sell/storefront/{self.project.id}'

    def mock_stripe(self, MockStripe):
        MockStripe.error = stripe_sdk.error
        MockStripe.billing.Meter.create.return_value = {'id': 'mtr_1'}
        MockStripe.Price.create.return_value = {'id': 'price_1'}
        MockStripe.checkout.Session.create.return_value = {'id': 'cs_u', 'url': 'https://x'}
        MockStripe.Subscription.retrieve.return_value = {
            'id': 'sub_1', 'customer': 'cus_1', 'status': 'active',
            'metadata': {'imagi_product_id': str(self.plan.id)},
            'items': {'data': [{'current_period_end': 1893456000}]},
        }

    def subscribe(self, MockStripe):
        self.mock_stripe(MockStripe)
        response = self.public.post(f'{self.storefront}/checkout/', {
            'items': [{'product_id': self.plan.id}], 'customer_email': 'Ada@Example.com',
            'success_url': 'http://localhost:5174/pricing/success?session_id={CHECKOUT_SESSION_ID}',
            'cancel_url': 'http://localhost:5174/pricing/cancel',
        }, format='json')
        self.assertEqual(response.status_code, 201, response.content)
        order = Order.objects.get(stripe_checkout_session_id='cs_u')
        SellService(self.project).apply_session(order, {
            'id': 'cs_u', 'status': 'complete', 'payment_status': 'no_payment_required',
            'customer': 'cus_1', 'subscription': 'sub_1', 'amount_total': 0,
            'customer_details': {'email': 'ada@example.com', 'name': 'Ada'},
        })
        return order

    def test_metered_checkout_creates_meter_and_price_once(self, MockStripe):
        order = self.subscribe(MockStripe)
        session = MockStripe.checkout.Session.create.call_args.kwargs
        self.assertEqual(session['mode'], 'subscription')
        self.assertEqual(session['line_items'], [{'price': 'price_1'}])
        self.assertEqual(session['subscription_data']['metadata']['imagi_product_id'],
                         str(self.plan.id))
        price = MockStripe.Price.create.call_args.kwargs
        self.assertEqual(price['unit_amount_decimal'], '0.1')
        self.assertEqual(price['recurring']['meter'], 'mtr_1')
        self.assertEqual(order.amount_total_cents, 0)

        # The next checkout reuses them; a price change makes a new price.
        self.public.post(f'{self.storefront}/checkout/',
                         {'items': [{'product_id': self.plan.id}]}, format='json')
        self.assertEqual(MockStripe.Price.create.call_count, 1)
        self.plan.refresh_from_db()
        self.plan.price_cents = 200
        self.plan.save()
        self.public.post(f'{self.storefront}/checkout/',
                         {'items': [{'product_id': self.plan.id}]}, format='json')
        self.assertEqual(MockStripe.Price.create.call_count, 2)
        self.assertEqual(MockStripe.billing.Meter.create.call_count, 1)

    def test_loopback_redirects_only_in_test_mode(self, MockStripe):
        self.mock_stripe(MockStripe)
        self.config.stripe_secret_key = 'sk_live_' + 'a' * 24
        self.config.save()
        response = self.public.post(f'{self.storefront}/checkout/', {
            'items': [{'product_id': self.plan.id}],
            'success_url': 'http://localhost:5174/pricing/success',
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_completed_checkout_records_subscription(self, MockStripe):
        order = self.subscribe(MockStripe)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.STATUS_PAID)
        subscription = self.project.sell_subscriptions.get()
        self.assertEqual(subscription.stripe_subscription_id, 'sub_1')
        self.assertEqual(subscription.customer_email, 'ada@example.com')
        self.assertEqual(subscription.product, self.plan)
        self.assertTrue(subscription.is_active)
        self.assertEqual(Customer.objects.get(project=self.project).stripe_customer_id, 'cus_1')

        response = self.client.get(f'{self.base}/subscriptions/?status=active')
        self.assertEqual(response.json()['total'], 1)
        self.assertEqual(response.json()['subscriptions'][0]['pricing_model'], 'usage')

    def test_usage_report_sends_meter_event_once_per_key(self, MockStripe):
        self.subscribe(MockStripe)
        MockStripe.billing.MeterEvent.create.return_value = {'identifier': 'x'}
        headers = {'Authorization': f'Bearer {self.server_key}'}
        body = {'customer_email': 'ada@example.com', 'quantity': 42, 'idempotency_key': 'job-7'}
        first = self.public.post(f'{self.storefront}/usage/', body, format='json', headers=headers)
        self.assertEqual(first.status_code, 201, first.content)
        again = self.public.post(f'{self.storefront}/usage/', body, format='json', headers=headers)
        self.assertEqual(again.json()['id'], first.json()['id'])
        self.assertEqual(MockStripe.billing.MeterEvent.create.call_count, 1)
        event = MockStripe.billing.MeterEvent.create.call_args.kwargs
        self.assertEqual(event['payload'], {'stripe_customer_id': 'cus_1', 'value': '42'})
        self.assertEqual(event['event_name'], f'imagi_p{self.project.id}_product_{self.plan.id}')

    def test_usage_requires_server_key_and_an_active_plan(self, MockStripe):
        self.mock_stripe(MockStripe)
        body = {'customer_email': 'ada@example.com', 'quantity': 1}
        response = self.public.post(f'{self.storefront}/usage/', body, format='json')
        self.assertEqual(response.status_code, 403)
        response = self.public.post(f'{self.storefront}/usage/', body, format='json',
                                    headers={'Authorization': 'Bearer imagi_sk_wrong'})
        self.assertEqual(response.status_code, 403)
        response = self.public.post(f'{self.storefront}/usage/', body, format='json',
                                    headers={'Authorization': f'Bearer {self.server_key}'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('no active pay-as-you-go plan', response.json()['error'])

    def test_failed_meter_event_is_not_counted(self, MockStripe):
        self.subscribe(MockStripe)
        MockStripe.billing.MeterEvent.create.side_effect = stripe_sdk.error.APIError('down')
        response = self.public.post(
            f'{self.storefront}/usage/',
            {'customer_email': 'ada@example.com', 'quantity': 1, 'idempotency_key': 'k'},
            format='json', headers={'Authorization': f'Bearer {self.server_key}'},
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(self.project.sell_usage_events.exists())

    def test_plan_check_for_the_apps_backend(self, MockStripe):
        self.subscribe(MockStripe)
        headers = {'Authorization': f'Bearer {self.server_key}'}
        response = self.public.get(f'{self.storefront}/subscriptions/?email=ADA@example.com',
                                   headers=headers)
        self.assertEqual(response.status_code, 200)
        plans = response.json()['subscriptions']
        self.assertEqual([p['product_id'] for p in plans], [self.plan.id])
        self.assertEqual(plans[0]['type'], 'usage')
        response = self.public.get(f'{self.storefront}/subscriptions/?email=bob@example.com',
                                   headers=headers)
        self.assertEqual(response.json()['subscriptions'], [])

    def test_session_status_reports_subscription_mode(self, MockStripe):
        order = self.subscribe(MockStripe)
        response = self.public.get(f'{self.storefront}/sessions/{order.stripe_checkout_session_id}/')
        self.assertEqual(response.json()['mode'], 'subscription')


class SubscriptionWebhookTests(SellAPITestCase):
    def test_subscription_events_update_the_mirror(self):
        plan = self.add_product('Pro', 2500, billing_interval='month')
        service = SellService(self.project)
        service.handle_webhook_event({'type': 'customer.subscription.created', 'data': {'object': {
            'id': 'sub_9', 'customer': 'cus_9', 'status': 'active',
            'metadata': {'imagi_product_id': str(plan.id)}, 'current_period_end': 1893456000,
        }}})
        service.handle_webhook_event({'type': 'customer.subscription.deleted', 'data': {'object': {
            'id': 'sub_9', 'customer': 'cus_9', 'status': 'canceled', 'metadata': {},
        }}})
        subscription = self.project.sell_subscriptions.get()
        self.assertEqual(subscription.status, 'canceled')
        self.assertEqual(subscription.product, plan)
        self.assertFalse(subscription.is_active)

    def test_overview_reports_subscribers_and_mrr(self):
        monthly = self.add_product('Pro', 2500, billing_interval='month')
        yearly = self.add_product('Team', 12000, billing_interval='year')
        from .models import Subscription
        Subscription.objects.create(project=self.project, product=monthly,
                                    stripe_subscription_id='s1', status='active')
        Subscription.objects.create(project=self.project, product=yearly,
                                    stripe_subscription_id='s2', status='trialing')
        Subscription.objects.create(project=self.project, product=monthly,
                                    stripe_subscription_id='s3', status='canceled')
        stats = self.client.get(f'{self.base}/overview/').json()['stats']
        self.assertEqual(stats['subscriptions_active'], 2)
        self.assertEqual(stats['mrr_cents'], 3500)
        self.assertEqual(stats['prices_by_model']['subscription'], 2)


class ConnectWebhookTests(SellAPITestCase):
    path = '/api/v1/sell/webhooks/connect/'

    def post(self, event, secret=TEST_WEBHOOK_SECRET):
        payload = json.dumps(event).encode()
        return APIClient().post(self.path, payload, content_type='application/json',
                                headers={'Stripe-Signature': stripe_signature(secret, payload)})

    @override_settings(STRIPE_CONNECT_WEBHOOK_SECRET=TEST_WEBHOOK_SECRET)
    def test_routes_events_by_connected_account(self):
        SellSettings.objects.create(project=self.project, connect_account_id='acct_123')
        order = Order.objects.create(project=self.project, amount_total_cents=500,
                                     stripe_checkout_session_id='cs_c')
        response = self.post({
            'id': 'evt_1', 'object': 'event', 'type': 'checkout.session.completed',
            'account': 'acct_123',
            'data': {'object': self.make_session_payload(order, id='cs_c')},
        })
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.STATUS_PAID)

        response = self.post({
            'id': 'evt_2', 'object': 'event', 'type': 'account.updated', 'account': 'acct_123',
            'data': {'object': {'id': 'acct_123', 'charges_enabled': True,
                                'payouts_enabled': True, 'details_submitted': True}},
        })
        self.assertTrue(SellSettings.objects.get(project=self.project).connect_charges_enabled)

    @override_settings(STRIPE_CONNECT_WEBHOOK_SECRET=TEST_WEBHOOK_SECRET)
    def test_rejects_bad_signature(self):
        response = self.post({'id': 'evt', 'type': 'x', 'account': 'acct_1'}, secret='whsec_other')
        self.assertEqual(response.status_code, 403)

    @override_settings(STRIPE_CONNECT_WEBHOOK_SECRET='')
    def test_rejects_when_unconfigured(self):
        response = self.post({'id': 'evt', 'type': 'x'})
        self.assertEqual(response.status_code, 403)


class StorefrontCorsTests(SellAPITestCase):
    """Generated apps run on their own origins and call the storefront API."""

    def test_storefront_allows_cross_origin_requests(self):
        self.add_product()
        public_client = APIClient()
        response = public_client.get(
            f'/api/v1/sell/storefront/{self.project.id}/products/',
            HTTP_ORIGIN='https://bloom-coffee.example.com',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get('Access-Control-Allow-Origin'),
            'https://bloom-coffee.example.com',
        )

    def test_owner_endpoints_keep_the_origin_allowlist(self):
        response = self.client.get(
            f'{self.base}/settings/',
            HTTP_ORIGIN='https://bloom-coffee.example.com',
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.headers.get('Access-Control-Allow-Origin'))
