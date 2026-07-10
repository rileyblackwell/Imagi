"""
Campaign orchestration and messaging workflows for the Marketing app.

Wraps the raw TwilioClient with everything project-specific: resolving the
campaign audience, personalizing message bodies, recording Message rows,
two-way inbox sends, inbound webhook handling, and status syncing.
"""

import datetime
import logging
import re
from xml.sax.saxutils import escape

from django.conf import settings as django_settings
from django.utils import timezone

from ..models import Campaign, Contact, Message
from .twilio_client import TwilioClient, TwilioError

logger = logging.getLogger(__name__)

# Twilio's window for scheduled messages: 15 minutes to 35 days out.
SCHEDULE_MIN_LEAD = datetime.timedelta(minutes=15)
SCHEDULE_MAX_LEAD = datetime.timedelta(days=35)

# Keywords customers text to manage consent (mirrors Twilio's own opt-out handling).
OPT_OUT_KEYWORDS = {'stop', 'stopall', 'unsubscribe', 'cancel', 'end', 'quit'}
OPT_IN_KEYWORDS = {'start', 'unstop', 'yes'}

# Message statuses that will never change again — skipped when syncing.
TERMINAL_STATUSES = Message.DELIVERED_STATUSES | Message.FAILED_STATUSES

PLACEHOLDER_PATTERN = re.compile(r'\{\{\s*(first_name|last_name|name)\s*\}\}')


class CampaignServiceError(Exception):
    """A user-facing problem (bad config, empty audience, Twilio rejection)."""


def webhook_base_url() -> str:
    base = getattr(django_settings, 'MARKETING_WEBHOOK_BASE_URL', '')
    return base.rstrip('/') if base else ''


def status_callback_url(project_id: int) -> str:
    """Public URL Twilio posts delivery updates to; empty when not configured."""
    base = webhook_base_url()
    if not base:
        return ''
    return f'{base}/api/v1/marketing/webhooks/{project_id}/status/'


def inbound_webhook_url(project_id: int) -> str:
    """Public URL to set as the phone number's incoming-message webhook."""
    base = webhook_base_url()
    if not base:
        return ''
    return f'{base}/api/v1/marketing/webhooks/{project_id}/inbound/'


def render_body(template: str, contact: Contact) -> str:
    """Fill {{first_name}} / {{last_name}} / {{name}} placeholders."""
    values = {
        'first_name': contact.first_name or 'there',
        'last_name': contact.last_name or '',
        'name': contact.display_name,
    }
    return PLACEHOLDER_PATTERN.sub(lambda match: values[match.group(1)], template)


class CampaignService:
    """Messaging operations for a single project."""

    def __init__(self, project):
        self.project = project
        self.config = getattr(project, 'marketing_settings', None)

    # -- setup ---------------------------------------------------------------

    def _client(self) -> TwilioClient:
        if not self.config or not self.config.is_configured:
            raise CampaignServiceError(
                'Twilio is not connected. Add your Account SID, auth token, and '
                'phone number in Marketing settings first.'
            )
        return TwilioClient(self.config.twilio_account_sid, self.config.twilio_auth_token)

    def verify(self) -> dict:
        """
        Check the stored credentials against Twilio and cache the account name.
        Returns account info plus the numbers available on the account.
        """
        client = self._client()
        try:
            account = client.fetch_account()
            numbers = client.list_phone_numbers()
        except TwilioError as exc:
            raise CampaignServiceError(f'Twilio rejected the credentials: {exc}') from exc

        self.config.account_friendly_name = account.get('friendly_name', '')
        self.config.last_verified_at = timezone.now()
        self.config.save(update_fields=['account_friendly_name', 'last_verified_at', 'updated_at'])

        return {
            'account_name': self.config.account_friendly_name,
            'account_status': account.get('status', ''),
            'phone_numbers': [
                {
                    'phone_number': number.get('phone_number', ''),
                    'friendly_name': number.get('friendly_name', ''),
                }
                for number in numbers
            ],
        }

    # -- audience --------------------------------------------------------------

    def recipients(self, campaign: Campaign):
        """
        Subscribed contacts matching the campaign's audience. Tag matching is
        done in Python because JSONField `contains` isn't supported on SQLite.
        """
        contacts = self.project.marketing_contacts.filter(consent=Contact.CONSENT_SUBSCRIBED)
        if campaign.audience_type == Campaign.AUDIENCE_TAGS:
            wanted = {str(tag).strip().lower() for tag in (campaign.audience_tags or []) if str(tag).strip()}
            if not wanted:
                return contacts.none()
            matching_ids = [
                contact.id for contact in contacts
                if wanted & contact.tag_set()
            ]
            return contacts.filter(id__in=matching_ids)
        return contacts

    # -- sending ---------------------------------------------------------------

    def send(self, campaign: Campaign, send_at=None) -> dict:
        """
        Dispatch a draft campaign now, or hand it to Twilio for scheduled
        delivery when `send_at` is given. Creates one Message row per recipient.
        """
        if campaign.status != Campaign.STATUS_DRAFT:
            raise CampaignServiceError('Only draft campaigns can be sent.')

        client = self._client()
        recipient_list = list(self.recipients(campaign))
        if not recipient_list:
            raise CampaignServiceError(
                'This campaign has no subscribed recipients. Add contacts or '
                'adjust the audience tags first.'
            )

        max_recipients = getattr(django_settings, 'MARKETING_MAX_CAMPAIGN_RECIPIENTS', 500)
        if len(recipient_list) > max_recipients:
            raise CampaignServiceError(
                f'This campaign would reach {len(recipient_list)} contacts, above the '
                f'per-send limit of {max_recipients}. Narrow the audience with tags.'
            )

        send_at_param = ''
        if send_at is not None:
            send_at_param = self._validate_schedule(campaign, send_at)

        campaign.status = Campaign.STATUS_SENDING
        campaign.started_at = timezone.now()
        campaign.scheduled_at = send_at
        campaign.save(update_fields=['status', 'started_at', 'scheduled_at', 'updated_at'])

        callback = status_callback_url(self.project.id)
        dispatched = 0
        failed = 0
        for contact in recipient_list:
            message = Message.objects.create(
                project=self.project,
                campaign=campaign,
                contact=contact,
                direction=Message.DIRECTION_OUTBOUND,
                channel=campaign.channel,
                body=render_body(campaign.body, contact),
                from_number=self.config.twilio_phone_number,
                to_number=contact.phone_number,
                status='queued',
            )
            try:
                if campaign.channel == Campaign.CHANNEL_VOICE:
                    payload = client.create_call(
                        to=contact.phone_number,
                        from_number=self.config.twilio_phone_number,
                        twiml=self._voice_twiml(message.body),
                        status_callback=callback,
                    )
                else:
                    payload = client.send_message(
                        to=contact.phone_number,
                        body=message.body,
                        from_number=self.config.twilio_phone_number,
                        messaging_service_sid=self.config.twilio_messaging_service_sid,
                        status_callback=callback,
                        send_at=send_at_param,
                    )
                message.twilio_sid = payload.get('sid', '')
                message.status = payload.get('status', 'queued') or 'queued'
                message.save(update_fields=['twilio_sid', 'status', 'updated_at'])
                dispatched += 1
            except TwilioError as exc:
                message.status = 'failed'
                message.error_code = str(exc.code or '')
                message.error_message = str(exc)
                message.save(update_fields=['status', 'error_code', 'error_message', 'updated_at'])
                failed += 1

        if dispatched == 0:
            campaign.status = Campaign.STATUS_FAILED
        elif send_at is not None:
            campaign.status = Campaign.STATUS_SCHEDULED
        else:
            campaign.status = Campaign.STATUS_SENT
        campaign.completed_at = None if send_at is not None else timezone.now()
        campaign.save(update_fields=['status', 'completed_at', 'updated_at'])

        return {'dispatched': dispatched, 'failed': failed}

    def _validate_schedule(self, campaign: Campaign, send_at) -> str:
        if campaign.channel != Campaign.CHANNEL_SMS:
            raise CampaignServiceError('Only SMS campaigns can be scheduled.')
        if not self.config.twilio_messaging_service_sid:
            raise CampaignServiceError(
                'Scheduling requires a Twilio Messaging Service SID — Twilio '
                'holds and delivers scheduled messages. Add one in Marketing '
                'settings, or send the campaign now instead.'
            )
        now = timezone.now()
        if send_at < now + SCHEDULE_MIN_LEAD:
            raise CampaignServiceError('Scheduled time must be at least 15 minutes from now.')
        if send_at > now + SCHEDULE_MAX_LEAD:
            raise CampaignServiceError('Scheduled time must be within 35 days.')
        return send_at.astimezone(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    def _voice_twiml(self, text: str) -> str:
        voice = self.config.voice if self.config else 'Polly.Joanna'
        return f'<Response><Say voice="{escape(voice)}">{escape(text)}</Say></Response>'

    def send_direct(self, contact: Contact, body: str) -> Message:
        """Send a one-off SMS from the inbox. Raises with Twilio's reason on failure."""
        client = self._client()
        message = Message.objects.create(
            project=self.project,
            contact=contact,
            direction=Message.DIRECTION_OUTBOUND,
            channel=Campaign.CHANNEL_SMS,
            body=body,
            from_number=self.config.twilio_phone_number,
            to_number=contact.phone_number,
            status='queued',
        )
        try:
            payload = client.send_message(
                to=contact.phone_number,
                body=body,
                from_number=self.config.twilio_phone_number,
                messaging_service_sid=self.config.twilio_messaging_service_sid,
                status_callback=status_callback_url(self.project.id),
            )
        except TwilioError as exc:
            message.status = 'failed'
            message.error_code = str(exc.code or '')
            message.error_message = str(exc)
            message.save(update_fields=['status', 'error_code', 'error_message', 'updated_at'])
            raise CampaignServiceError(f'Twilio could not send the message: {exc}') from exc

        message.twilio_sid = payload.get('sid', '')
        message.status = payload.get('status', 'queued') or 'queued'
        message.save(update_fields=['twilio_sid', 'status', 'updated_at'])
        return message

    # -- lifecycle ---------------------------------------------------------------

    def cancel(self, campaign: Campaign) -> dict:
        """Cancel a scheduled campaign by canceling each not-yet-sent message."""
        if campaign.status != Campaign.STATUS_SCHEDULED:
            raise CampaignServiceError('Only scheduled campaigns can be canceled.')

        client = self._client()
        canceled = 0
        errors = 0
        pending = campaign.messages.exclude(twilio_sid='').exclude(status__in=TERMINAL_STATUSES)
        for message in pending:
            try:
                client.cancel_message(message.twilio_sid)
                message.status = 'canceled'
                message.save(update_fields=['status', 'updated_at'])
                canceled += 1
            except TwilioError as exc:
                logger.warning(f'Could not cancel scheduled message {message.twilio_sid}: {exc}')
                errors += 1

        campaign.status = Campaign.STATUS_CANCELED
        campaign.completed_at = timezone.now()
        campaign.save(update_fields=['status', 'completed_at', 'updated_at'])
        return {'canceled': canceled, 'errors': errors}

    def sync_statuses(self, campaign: Campaign) -> dict:
        """
        Pull current delivery statuses from Twilio for in-flight messages.
        The fallback when status webhooks aren't reachable (e.g. local dev).
        """
        client = self._client()
        updated = 0
        pending = campaign.messages.exclude(twilio_sid='').exclude(status__in=TERMINAL_STATUSES)
        for message in pending:
            try:
                if message.channel == Campaign.CHANNEL_VOICE:
                    payload = client.fetch_call(message.twilio_sid)
                else:
                    payload = client.fetch_message(message.twilio_sid)
            except TwilioError as exc:
                logger.warning(f'Could not sync message {message.twilio_sid}: {exc}')
                continue
            new_status = payload.get('status', '')
            if new_status and new_status != message.status:
                message.status = new_status
                message.error_code = str(payload.get('error_code') or '')
                message.error_message = payload.get('error_message') or ''
                message.save(update_fields=['status', 'error_code', 'error_message', 'updated_at'])
                updated += 1

        # A scheduled campaign whose messages have all left Twilio's queue is done.
        if campaign.status == Campaign.STATUS_SCHEDULED:
            still_scheduled = campaign.messages.filter(status__in=['scheduled', 'accepted', 'queued']).exists()
            if not still_scheduled:
                campaign.status = Campaign.STATUS_SENT
                campaign.completed_at = timezone.now()
                campaign.save(update_fields=['status', 'completed_at', 'updated_at'])

        return {'updated': updated}

    # -- webhooks ---------------------------------------------------------------

    def apply_status_update(self, params: dict) -> bool:
        """
        Apply a Twilio status callback (message or call) to the matching
        Message row. Returns True when a row was updated.
        """
        twilio_sid = params.get('MessageSid') or params.get('SmsSid') or params.get('CallSid') or ''
        new_status = params.get('MessageStatus') or params.get('SmsStatus') or params.get('CallStatus') or ''
        if not twilio_sid or not new_status:
            return False
        message = self.project.marketing_messages.filter(twilio_sid=twilio_sid).first()
        if not message:
            return False
        message.status = new_status
        error_code = params.get('ErrorCode', '')
        if error_code:
            message.error_code = str(error_code)
        message.save(update_fields=['status', 'error_code', 'updated_at'])
        return True

    def record_inbound(self, params: dict) -> Message:
        """
        Record an incoming SMS: find or create the contact, store the message,
        and honor STOP/START consent keywords.
        """
        from_number = params.get('From', '')
        body = params.get('Body', '') or ''

        contact = None
        if from_number:
            contact = self.project.marketing_contacts.filter(phone_number=from_number).first()
            if not contact:
                contact = Contact.objects.create(
                    project=self.project,
                    phone_number=from_number,
                    source='inbound',
                )

        if contact:
            keyword = body.strip().lower()
            if keyword in OPT_OUT_KEYWORDS and contact.consent != Contact.CONSENT_UNSUBSCRIBED:
                contact.consent = Contact.CONSENT_UNSUBSCRIBED
                contact.save(update_fields=['consent', 'updated_at'])
            elif keyword in OPT_IN_KEYWORDS and contact.consent != Contact.CONSENT_SUBSCRIBED:
                contact.consent = Contact.CONSENT_SUBSCRIBED
                contact.save(update_fields=['consent', 'updated_at'])

        return Message.objects.create(
            project=self.project,
            contact=contact,
            direction=Message.DIRECTION_INBOUND,
            channel=Campaign.CHANNEL_SMS,
            body=body,
            from_number=from_number,
            to_number=params.get('To', ''),
            twilio_sid=params.get('MessageSid', '') or params.get('SmsSid', ''),
            status='received',
        )
