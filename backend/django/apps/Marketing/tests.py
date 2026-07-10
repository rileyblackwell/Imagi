"""
Tests for the Marketing app: credential handling, audience management,
campaign sending (with Twilio mocked), and webhook processing.
"""

import base64
import hashlib
import hmac
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase

from apps.Products.Imagi.ProjectManager.models import Project

from .models import (
    Campaign,
    Contact,
    MarketingSettings,
    Message,
    decrypt_secret,
    encrypt_secret,
)
from .services.twilio_client import TwilioError

User = get_user_model()

TEST_ACCOUNT_SID = 'AC' + 'a' * 32
TEST_MESSAGING_SERVICE_SID = 'MG' + 'b' * 32


def twilio_signature(auth_token: str, url: str, params: dict) -> str:
    """Compute an X-Twilio-Signature the way Twilio does."""
    payload = url + ''.join(key + value for key, value in sorted(params.items()))
    digest = hmac.new(auth_token.encode(), payload.encode('utf-8'), hashlib.sha1).digest()
    return base64.b64encode(digest).decode()


class MarketingAPITestCase(APITestCase):
    """Shared fixtures: a user, their project, and an authenticated client."""

    def setUp(self):
        self.user = User.objects.create_user(username='owner', password='pass12345')
        self.other_user = User.objects.create_user(username='intruder', password='pass12345')
        self.project = Project.objects.create(name='Bloom Coffee', user=self.user)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.base = f'/api/v1/marketing/projects/{self.project.id}'

    def configure_twilio(self, **overrides):
        settings_obj, _ = MarketingSettings.objects.get_or_create(project=self.project)
        settings_obj.twilio_account_sid = overrides.get('account_sid', TEST_ACCOUNT_SID)
        settings_obj.twilio_auth_token = overrides.get('auth_token', 'secret-token')
        settings_obj.twilio_phone_number = overrides.get('phone_number', '+15550001111')
        settings_obj.twilio_messaging_service_sid = overrides.get('messaging_service_sid', '')
        settings_obj.save()
        return settings_obj

    def add_contact(self, phone, first_name='', tags=None, consent=Contact.CONSENT_SUBSCRIBED):
        return Contact.objects.create(
            project=self.project,
            phone_number=phone,
            first_name=first_name,
            tags=tags or [],
            consent=consent,
        )


class SecretEncryptionTests(APITestCase):
    def test_round_trip(self):
        token = encrypt_secret('super-secret')
        self.assertNotEqual(token, 'super-secret')
        self.assertNotIn('super-secret', token)
        self.assertEqual(decrypt_secret(token), 'super-secret')

    def test_empty_and_garbage(self):
        self.assertEqual(encrypt_secret(''), '')
        self.assertEqual(decrypt_secret(''), '')
        self.assertEqual(decrypt_secret('not-a-fernet-token'), '')


class MarketingSettingsAPITests(MarketingAPITestCase):
    def test_get_creates_default_settings(self):
        response = self.client.get(f'{self.base}/settings/')
        self.assertEqual(response.status_code, 200)
        data = response.json()['settings']
        self.assertFalse(data['is_configured'])
        self.assertFalse(data['twilio_auth_token_set'])
        self.assertNotIn('twilio_auth_token', data)

    def test_update_stores_encrypted_token_and_masks_it(self):
        response = self.client.put(f'{self.base}/settings/', {
            'twilio_account_sid': TEST_ACCOUNT_SID,
            'twilio_auth_token': 'my-auth-token',
            'twilio_phone_number': '+15550001111',
        }, format='json')
        self.assertEqual(response.status_code, 200)
        data = response.json()['settings']
        self.assertTrue(data['is_configured'])
        self.assertTrue(data['twilio_auth_token_set'])
        self.assertNotIn('twilio_auth_token', data)

        stored = MarketingSettings.objects.get(project=self.project)
        self.assertNotIn('my-auth-token', stored.twilio_auth_token_encrypted)
        self.assertEqual(stored.twilio_auth_token, 'my-auth-token')

    def test_blank_token_keeps_existing_secret(self):
        self.configure_twilio()
        response = self.client.put(f'{self.base}/settings/', {
            'twilio_auth_token': '',
            'twilio_phone_number': '+15550002222',
        }, format='json')
        self.assertEqual(response.status_code, 200)
        stored = MarketingSettings.objects.get(project=self.project)
        self.assertEqual(stored.twilio_auth_token, 'secret-token')
        self.assertEqual(stored.twilio_phone_number, '+15550002222')

    def test_clearing_account_sid_wipes_token(self):
        self.configure_twilio()
        response = self.client.put(
            f'{self.base}/settings/', {'twilio_account_sid': ''}, format='json'
        )
        self.assertEqual(response.status_code, 200)
        stored = MarketingSettings.objects.get(project=self.project)
        self.assertEqual(stored.twilio_auth_token_encrypted, '')

    def test_rejects_malformed_account_sid(self):
        response = self.client.put(
            f'{self.base}/settings/', {'twilio_account_sid': 'not-a-sid'}, format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_other_users_project_is_not_found(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(f'{self.base}/settings/')
        self.assertEqual(response.status_code, 404)

    def test_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(f'{self.base}/settings/')
        self.assertIn(response.status_code, (401, 403))


class ContactAPITests(MarketingAPITestCase):
    def test_create_list_update_delete(self):
        response = self.client.post(f'{self.base}/contacts/', {
            'first_name': 'Ada',
            'last_name': 'Lovelace',
            'phone_number': '+15551230001',
            'email': 'ada@example.com',
            'tags': ['vip', 'VIP', '  early  '],
        }, format='json')
        self.assertEqual(response.status_code, 201)
        contact = response.json()['contact']
        self.assertEqual(contact['display_name'], 'Ada Lovelace')
        # Tags are trimmed and case-insensitively de-duplicated.
        self.assertEqual(contact['tags'], ['vip', 'early'])

        response = self.client.get(f'{self.base}/contacts/', {'search': 'ada'})
        self.assertEqual(response.json()['total'], 1)

        contact_id = contact['id']
        response = self.client.patch(
            f'{self.base}/contacts/{contact_id}/', {'first_name': 'Adah'}, format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['contact']['first_name'], 'Adah')

        response = self.client.delete(f'{self.base}/contacts/{contact_id}/')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.project.marketing_contacts.count(), 0)

    def test_rejects_duplicate_and_invalid_phone(self):
        self.add_contact('+15551230001')
        response = self.client.post(
            f'{self.base}/contacts/', {'phone_number': '+15551230001'}, format='json'
        )
        self.assertEqual(response.status_code, 400)
        response = self.client.post(
            f'{self.base}/contacts/', {'phone_number': '555-123'}, format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_tag_filter(self):
        self.add_contact('+15551230001', tags=['VIP'])
        self.add_contact('+15551230002', tags=['newsletter'])
        response = self.client.get(f'{self.base}/contacts/', {'tag': 'vip'})
        payload = response.json()
        self.assertEqual(payload['total'], 1)
        self.assertEqual(payload['contacts'][0]['phone_number'], '+15551230001')

    def test_import_skips_bad_rows(self):
        self.add_contact('+15551230001')
        response = self.client.post(f'{self.base}/contacts/import/', {
            'contacts': [
                {'first_name': 'New', 'phone_number': '+15551230002', 'tags': 'vip, spring'},
                {'phone_number': '+15551230001'},          # duplicate of existing
                {'phone_number': 'garbage'},               # invalid
                {'phone_number': '+15551230003', 'email': 'not-an-email'},
                {'phone_number': '+15551230002'},          # duplicate within batch
            ],
        }, format='json')
        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertEqual(payload['created'], 2)
        self.assertEqual(len(payload['skipped']), 3)
        imported = self.project.marketing_contacts.get(phone_number='+15551230002')
        self.assertEqual(imported.tags, ['vip', 'spring'])
        self.assertEqual(imported.source, 'import')
        # Invalid email is dropped, not fatal.
        self.assertEqual(
            self.project.marketing_contacts.get(phone_number='+15551230003').email, ''
        )

    def test_tags_endpoint_aggregates(self):
        self.add_contact('+15551230001', tags=['VIP'])
        self.add_contact('+15551230002', tags=['vip', 'beta'])
        response = self.client.get(f'{self.base}/tags/')
        tags = {item['tag'].lower(): item['count'] for item in response.json()['tags']}
        self.assertEqual(tags, {'vip': 2, 'beta': 1})


@patch('apps.Marketing.services.campaign_service.TwilioClient')
class CampaignAPITests(MarketingAPITestCase):
    def setUp(self):
        super().setUp()
        self.configure_twilio()

    def make_campaign(self, **overrides):
        payload = {
            'name': 'Grand opening',
            'channel': 'sms',
            'body': 'Hi {{first_name}}, we open Friday!',
            'audience_type': 'all',
        }
        payload.update(overrides)
        response = self.client.post(f'{self.base}/campaigns/', payload, format='json')
        self.assertEqual(response.status_code, 201, response.content)
        return response.json()['campaign']

    def test_send_now_creates_messages_and_personalizes(self, MockClient):
        client = MockClient.return_value
        client.send_message.return_value = {'sid': 'SM123', 'status': 'queued'}

        self.add_contact('+15551230001', first_name='Ada')
        self.add_contact('+15551230002', consent=Contact.CONSENT_UNSUBSCRIBED)
        campaign = self.make_campaign()

        response = self.client.post(f'{self.base}/campaigns/{campaign["id"]}/send/', {}, format='json')
        self.assertEqual(response.status_code, 200, response.content)
        payload = response.json()
        self.assertEqual(payload['dispatched'], 1)
        self.assertEqual(payload['failed'], 0)
        self.assertEqual(payload['campaign']['status'], 'sent')
        self.assertEqual(payload['campaign']['stats']['recipients'], 1)

        # Only the subscribed contact got a message, with placeholders filled.
        message = Message.objects.get(campaign_id=campaign['id'])
        self.assertEqual(message.to_number, '+15551230001')
        self.assertEqual(message.body, 'Hi Ada, we open Friday!')
        self.assertEqual(message.twilio_sid, 'SM123')
        client.send_message.assert_called_once()

    def test_send_requires_recipients(self, MockClient):
        campaign = self.make_campaign()
        response = self.client.post(f'{self.base}/campaigns/{campaign["id"]}/send/', {}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('recipients', response.json()['error'])

    def test_send_requires_twilio_config(self, MockClient):
        MarketingSettings.objects.filter(project=self.project).delete()
        self.add_contact('+15551230001')
        campaign = self.make_campaign()
        response = self.client.post(f'{self.base}/campaigns/{campaign["id"]}/send/', {}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Twilio is not connected', response.json()['error'])

    def test_tag_audience_targets_matching_contacts(self, MockClient):
        client = MockClient.return_value
        client.send_message.return_value = {'sid': 'SM1', 'status': 'queued'}
        self.add_contact('+15551230001', tags=['VIP'])
        self.add_contact('+15551230002', tags=['other'])
        campaign = self.make_campaign(audience_type='tags', audience_tags=['vip'])

        response = self.client.get(f'{self.base}/campaigns/{campaign["id"]}/recipients/')
        self.assertEqual(response.json()['recipients'], 1)

        response = self.client.post(f'{self.base}/campaigns/{campaign["id"]}/send/', {}, format='json')
        self.assertEqual(response.json()['dispatched'], 1)
        self.assertEqual(
            Message.objects.get(campaign_id=campaign['id']).to_number, '+15551230001'
        )

    def test_voice_campaign_places_calls_with_twiml(self, MockClient):
        client = MockClient.return_value
        client.create_call.return_value = {'sid': 'CA1', 'status': 'queued'}
        self.add_contact('+15551230001', first_name='Ada')
        campaign = self.make_campaign(channel='voice', body='Hello {{first_name}}, sale on Friday.')

        response = self.client.post(f'{self.base}/campaigns/{campaign["id"]}/send/', {}, format='json')
        self.assertEqual(response.status_code, 200, response.content)
        _, kwargs = client.create_call.call_args
        self.assertIn('<Say', kwargs['twiml'])
        self.assertIn('Hello Ada, sale on Friday.', kwargs['twiml'])
        client.send_message.assert_not_called()

    def test_partial_twilio_failure_still_completes(self, MockClient):
        client = MockClient.return_value
        client.send_message.side_effect = [
            {'sid': 'SM1', 'status': 'queued'},
            TwilioError('The number is unverified', status=400, code=21608),
        ]
        self.add_contact('+15551230001')
        self.add_contact('+15551230002')
        campaign = self.make_campaign()

        response = self.client.post(f'{self.base}/campaigns/{campaign["id"]}/send/', {}, format='json')
        payload = response.json()
        self.assertEqual(payload['dispatched'], 1)
        self.assertEqual(payload['failed'], 1)
        failed = Message.objects.get(status='failed')
        self.assertEqual(failed.error_code, '21608')

    def test_schedule_requires_messaging_service(self, MockClient):
        self.add_contact('+15551230001')
        campaign = self.make_campaign()
        response = self.client.post(f'{self.base}/campaigns/{campaign["id"]}/send/', {
            'send_at': '2099-01-01T12:00:00Z',
        }, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Messaging Service', response.json()['error'])

    def test_schedule_within_window_via_messaging_service(self, MockClient):
        import datetime
        from django.utils import timezone
        client = MockClient.return_value
        client.send_message.return_value = {'sid': 'SM1', 'status': 'scheduled'}
        self.configure_twilio(messaging_service_sid=TEST_MESSAGING_SERVICE_SID)
        self.add_contact('+15551230001')
        campaign = self.make_campaign()

        send_at = (timezone.now() + datetime.timedelta(hours=2)).isoformat()
        response = self.client.post(
            f'{self.base}/campaigns/{campaign["id"]}/send/', {'send_at': send_at}, format='json'
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()['campaign']['status'], 'scheduled')
        _, kwargs = client.send_message.call_args
        self.assertTrue(kwargs['send_at'])
        self.assertEqual(kwargs['messaging_service_sid'], TEST_MESSAGING_SERVICE_SID)

        # Cancel it: pending scheduled messages are canceled through Twilio.
        client.cancel_message.return_value = {'sid': 'SM1', 'status': 'canceled'}
        response = self.client.post(f'{self.base}/campaigns/{campaign["id"]}/cancel/', {}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['campaign']['status'], 'canceled')
        self.assertEqual(Message.objects.get(twilio_sid='SM1').status, 'canceled')

    def test_sync_pulls_statuses(self, MockClient):
        client = MockClient.return_value
        client.send_message.return_value = {'sid': 'SM1', 'status': 'queued'}
        client.fetch_message.return_value = {'sid': 'SM1', 'status': 'delivered'}
        self.add_contact('+15551230001')
        campaign = self.make_campaign()
        self.client.post(f'{self.base}/campaigns/{campaign["id"]}/send/', {}, format='json')

        response = self.client.post(f'{self.base}/campaigns/{campaign["id"]}/sync/', {}, format='json')
        self.assertEqual(response.json()['updated'], 1)
        self.assertEqual(Message.objects.get(twilio_sid='SM1').status, 'delivered')
        self.assertEqual(response.json()['campaign']['stats']['delivered'], 1)

    def test_only_drafts_can_be_edited_or_resent(self, MockClient):
        client = MockClient.return_value
        client.send_message.return_value = {'sid': 'SM1', 'status': 'queued'}
        self.add_contact('+15551230001')
        campaign = self.make_campaign()
        self.client.post(f'{self.base}/campaigns/{campaign["id"]}/send/', {}, format='json')

        response = self.client.patch(
            f'{self.base}/campaigns/{campaign["id"]}/', {'name': 'Renamed'}, format='json'
        )
        self.assertEqual(response.status_code, 400)
        response = self.client.post(f'{self.base}/campaigns/{campaign["id"]}/send/', {}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_tag_audience_requires_tags(self, MockClient):
        response = self.client.post(f'{self.base}/campaigns/', {
            'name': 'Broken',
            'channel': 'sms',
            'body': 'Hello',
            'audience_type': 'tags',
            'audience_tags': [],
        }, format='json')
        self.assertEqual(response.status_code, 400)


@patch('apps.Marketing.services.campaign_service.TwilioClient')
class InboxAPITests(MarketingAPITestCase):
    def setUp(self):
        super().setUp()
        self.configure_twilio()

    def test_direct_message_and_conversations(self, MockClient):
        client = MockClient.return_value
        client.send_message.return_value = {'sid': 'SM9', 'status': 'queued'}
        contact = self.add_contact('+15551230001', first_name='Ada')

        response = self.client.post(
            f'{self.base}/contacts/{contact.id}/messages/', {'body': 'Thanks for visiting!'},
            format='json',
        )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(response.json()['message']['direction'], 'outbound')

        response = self.client.get(f'{self.base}/conversations/')
        conversations = response.json()['conversations']
        self.assertEqual(len(conversations), 1)
        self.assertEqual(conversations[0]['last_message_body'], 'Thanks for visiting!')

        response = self.client.get(f'{self.base}/contacts/{contact.id}/messages/')
        self.assertEqual(len(response.json()['messages']), 1)

    def test_cannot_message_unsubscribed_contact(self, MockClient):
        contact = self.add_contact('+15551230001', consent=Contact.CONSENT_UNSUBSCRIBED)
        response = self.client.post(
            f'{self.base}/contacts/{contact.id}/messages/', {'body': 'Hello'}, format='json'
        )
        self.assertEqual(response.status_code, 400)


class WebhookTests(MarketingAPITestCase):
    def setUp(self):
        super().setUp()
        self.settings_obj = self.configure_twilio(auth_token='webhook-token')
        self.webhook_client = APIClient()  # unauthenticated, like Twilio

    def post_signed(self, path, params, token='webhook-token'):
        url = f'http://testserver{path}'
        signature = twilio_signature(token, url, params)
        return self.webhook_client.post(
            path, params, format='multipart', headers={'X-Twilio-Signature': signature}
        )

    def test_status_callback_updates_message(self):
        contact = self.add_contact('+15551230001')
        message = Message.objects.create(
            project=self.project,
            contact=contact,
            direction=Message.DIRECTION_OUTBOUND,
            channel='sms',
            twilio_sid='SM42',
            status='sent',
        )
        path = f'/api/v1/marketing/webhooks/{self.project.id}/status/'
        response = self.post_signed(path, {'MessageSid': 'SM42', 'MessageStatus': 'delivered'})
        self.assertEqual(response.status_code, 204)
        message.refresh_from_db()
        self.assertEqual(message.status, 'delivered')

    def test_rejects_bad_signature(self):
        path = f'/api/v1/marketing/webhooks/{self.project.id}/status/'
        response = self.post_signed(
            path, {'MessageSid': 'SM42', 'MessageStatus': 'delivered'}, token='wrong-token'
        )
        self.assertEqual(response.status_code, 403)

    def test_inbound_creates_contact_and_message(self):
        path = f'/api/v1/marketing/webhooks/{self.project.id}/inbound/'
        response = self.post_signed(path, {
            'MessageSid': 'SM77',
            'From': '+15559998888',
            'To': '+15550001111',
            'Body': 'Do you deliver?',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('<Response></Response>', response.content.decode())
        contact = self.project.marketing_contacts.get(phone_number='+15559998888')
        self.assertEqual(contact.source, 'inbound')
        message = self.project.marketing_messages.get(twilio_sid='SM77')
        self.assertEqual(message.direction, 'inbound')
        self.assertEqual(message.body, 'Do you deliver?')

    def test_stop_and_start_manage_consent(self):
        contact = self.add_contact('+15551230001')
        path = f'/api/v1/marketing/webhooks/{self.project.id}/inbound/'

        self.post_signed(path, {'MessageSid': 'SM1', 'From': contact.phone_number, 'Body': 'STOP'})
        contact.refresh_from_db()
        self.assertEqual(contact.consent, Contact.CONSENT_UNSUBSCRIBED)

        self.post_signed(path, {'MessageSid': 'SM2', 'From': contact.phone_number, 'Body': 'START'})
        contact.refresh_from_db()
        self.assertEqual(contact.consent, Contact.CONSENT_SUBSCRIBED)


class OverviewAPITests(MarketingAPITestCase):
    def test_overview_counts(self):
        self.configure_twilio()
        contact = self.add_contact('+15551230001')
        self.add_contact('+15551230002', consent=Contact.CONSENT_UNSUBSCRIBED)
        campaign = Campaign.objects.create(
            project=self.project, name='Launch', body='Hi', status=Campaign.STATUS_SENT
        )
        Message.objects.create(
            project=self.project, contact=contact, campaign=campaign,
            direction=Message.DIRECTION_OUTBOUND, channel='sms', status='delivered',
        )
        Message.objects.create(
            project=self.project, contact=contact,
            direction=Message.DIRECTION_INBOUND, channel='sms', status='received',
        )

        response = self.client.get(f'{self.base}/overview/')
        self.assertEqual(response.status_code, 200)
        stats = response.json()['stats']
        self.assertTrue(stats['configured'])
        self.assertEqual(stats['contacts_total'], 2)
        self.assertEqual(stats['contacts_subscribed'], 1)
        self.assertEqual(stats['campaigns_total'], 1)
        self.assertEqual(stats['messages_sent_30d'], 1)
        self.assertEqual(stats['messages_delivered_30d'], 1)
        self.assertEqual(stats['replies_30d'], 1)
        self.assertEqual(len(response.json()['recent_campaigns']), 1)
        self.assertEqual(len(response.json()['recent_inbound']), 1)
