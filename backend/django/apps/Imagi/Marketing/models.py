"""
Models for the Marketing app.

Everything here is scoped to a ProjectManager Project: each user project
(business) gets its own Twilio configuration, audience of contacts, campaigns,
and message history. Twilio is the delivery layer — SMS/MMS campaigns and
two-way texting via Programmable Messaging, voice broadcasts via
Programmable Voice.

The advertising side connects the project's own Google Ads and Meta Ads
accounts: AdConnection stores the (encrypted) API credentials per provider,
and AdCampaign is a local, periodically synced mirror of the campaigns and
their performance so the workspace can show one unified ads dashboard and
push pause/resume back to the platform.
"""

import base64
import hashlib
import json
import logging

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

logger = logging.getLogger(__name__)

# E.164 format, e.g. +15551234567 — the only format Twilio accepts.
phone_validator = RegexValidator(
    regex=r'^\+[1-9]\d{1,14}$',
    message='Phone number must be in E.164 format, e.g. +15551234567',
)


def _fernet():
    """Fernet keyed off SECRET_KEY, used to encrypt Twilio credentials at rest."""
    from cryptography.fernet import Fernet
    digest = hashlib.sha256(
        ('imagi.marketing.twilio:' + settings.SECRET_KEY).encode()
    ).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def encrypt_secret(value: str) -> str:
    if not value:
        return ''
    return _fernet().encrypt(value.encode()).decode()


def decrypt_secret(token: str) -> str:
    if not token:
        return ''
    try:
        return _fernet().decrypt(token.encode()).decode()
    except Exception:
        # Wrong SECRET_KEY or corrupted value — treat as unset so the user
        # can re-enter the credential rather than crash.
        logger.warning('Could not decrypt a stored Twilio credential; treating it as unset.')
        return ''


class MarketingSettings(models.Model):
    """Per-project Twilio configuration for the marketing workspace."""

    # A small allowlist of Twilio text-to-speech voices for voice broadcasts.
    VOICE_CHOICES = [
        ('Polly.Joanna', 'Joanna (female, US English)'),
        ('Polly.Matthew', 'Matthew (male, US English)'),
        ('Polly.Amy', 'Amy (female, British English)'),
        ('Polly.Brian', 'Brian (male, British English)'),
        ('alice', 'Alice (classic)'),
    ]

    project = models.OneToOneField(
        'ProjectManager.Project',
        on_delete=models.CASCADE,
        related_name='marketing_settings',
    )
    twilio_account_sid = models.CharField(max_length=64, blank=True, default='')
    # Encrypted with a SECRET_KEY-derived Fernet key; use the
    # `twilio_auth_token` property to read/write the plaintext value.
    twilio_auth_token_encrypted = models.TextField(blank=True, default='')
    twilio_phone_number = models.CharField(
        max_length=20,
        blank=True,
        default='',
        validators=[phone_validator],
        help_text='Twilio phone number used as the sender, in E.164 format',
    )
    twilio_messaging_service_sid = models.CharField(
        max_length=64,
        blank=True,
        default='',
        help_text='Optional Messaging Service SID; required for scheduled campaigns',
    )
    voice = models.CharField(
        max_length=50,
        choices=VOICE_CHOICES,
        default='Polly.Joanna',
        help_text='Text-to-speech voice used for voice broadcasts',
    )
    account_friendly_name = models.CharField(max_length=255, blank=True, default='')
    last_verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Marketing Settings'
        verbose_name_plural = 'Marketing Settings'

    def __str__(self):
        return f"Marketing settings for {self.project.name}"

    @property
    def twilio_auth_token(self) -> str:
        return decrypt_secret(self.twilio_auth_token_encrypted)

    @twilio_auth_token.setter
    def twilio_auth_token(self, value: str):
        self.twilio_auth_token_encrypted = encrypt_secret(value)

    @property
    def is_configured(self) -> bool:
        """True when there are enough credentials to send messages."""
        return bool(
            self.twilio_account_sid
            and self.twilio_auth_token_encrypted
            and (self.twilio_phone_number or self.twilio_messaging_service_sid)
        )


class Contact(models.Model):
    """A person in a project's marketing audience."""

    CONSENT_SUBSCRIBED = 'subscribed'
    CONSENT_UNSUBSCRIBED = 'unsubscribed'
    CONSENT_CHOICES = [
        (CONSENT_SUBSCRIBED, 'Subscribed'),
        (CONSENT_UNSUBSCRIBED, 'Unsubscribed'),
    ]

    SOURCE_CHOICES = [
        ('manual', 'Added manually'),
        ('import', 'Imported'),
        ('inbound', 'Inbound message'),
    ]

    project = models.ForeignKey(
        'ProjectManager.Project',
        on_delete=models.CASCADE,
        related_name='marketing_contacts',
    )
    first_name = models.CharField(max_length=100, blank=True, default='')
    last_name = models.CharField(max_length=100, blank=True, default='')
    phone_number = models.CharField(max_length=20, validators=[phone_validator])
    email = models.EmailField(blank=True, default='')
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text='List of tag strings used for audience segmentation',
    )
    consent = models.CharField(
        max_length=20,
        choices=CONSENT_CHOICES,
        default=CONSENT_SUBSCRIBED,
        help_text='Only subscribed contacts receive campaigns',
    )
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='manual')
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'phone_number'],
                name='unique_marketing_contact_phone_per_project',
            )
        ]
        indexes = [
            models.Index(fields=['project', 'consent']),
        ]

    def __str__(self):
        return f"{self.display_name} ({self.project.name})"

    @property
    def display_name(self) -> str:
        name = f"{self.first_name} {self.last_name}".strip()
        return name or self.phone_number

    def tag_set(self) -> set:
        """Lowercased tags for case-insensitive matching."""
        return {str(tag).strip().lower() for tag in (self.tags or []) if str(tag).strip()}


class Campaign(models.Model):
    """An outbound SMS blast or voice broadcast to a segment of the audience."""

    CHANNEL_SMS = 'sms'
    CHANNEL_VOICE = 'voice'
    CHANNEL_CHOICES = [
        (CHANNEL_SMS, 'Text message'),
        (CHANNEL_VOICE, 'Voice call'),
    ]

    AUDIENCE_ALL = 'all'
    AUDIENCE_TAGS = 'tags'
    AUDIENCE_CHOICES = [
        (AUDIENCE_ALL, 'All subscribed contacts'),
        (AUDIENCE_TAGS, 'Contacts with any of the selected tags'),
    ]

    STATUS_DRAFT = 'draft'
    STATUS_SCHEDULED = 'scheduled'
    STATUS_SENDING = 'sending'
    STATUS_SENT = 'sent'
    STATUS_FAILED = 'failed'
    STATUS_CANCELED = 'canceled'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_SCHEDULED, 'Scheduled'),
        (STATUS_SENDING, 'Sending'),
        (STATUS_SENT, 'Sent'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_CANCELED, 'Canceled'),
    ]

    project = models.ForeignKey(
        'ProjectManager.Project',
        on_delete=models.CASCADE,
        related_name='marketing_campaigns',
    )
    name = models.CharField(max_length=255)
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES, default=CHANNEL_SMS)
    body = models.TextField(
        help_text='Message text (SMS) or spoken script (voice). '
                  'Supports {{first_name}}, {{last_name}} and {{name}} placeholders.',
    )
    audience_type = models.CharField(max_length=10, choices=AUDIENCE_CHOICES, default=AUDIENCE_ALL)
    audience_tags = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'status']),
        ]

    def __str__(self):
        return f"{self.name} [{self.get_status_display()}]"

    @property
    def is_editable(self) -> bool:
        return self.status == self.STATUS_DRAFT


class Message(models.Model):
    """
    One SMS or voice interaction, inbound or outbound.

    Campaign sends create one row per recipient; direct replies from the inbox
    and incoming messages from customers land here too, so a contact's thread
    is simply their messages ordered by time. `status` stores Twilio's raw
    status string (queued, sent, delivered, failed, completed, ...).
    """

    DIRECTION_OUTBOUND = 'outbound'
    DIRECTION_INBOUND = 'inbound'
    DIRECTION_CHOICES = [
        (DIRECTION_OUTBOUND, 'Outbound'),
        (DIRECTION_INBOUND, 'Inbound'),
    ]

    CHANNEL_CHOICES = Campaign.CHANNEL_CHOICES

    # Buckets of Twilio statuses used for delivery stats. Anything else counts
    # as pending/in-flight.
    DELIVERED_STATUSES = {'delivered', 'read', 'completed'}
    FAILED_STATUSES = {'failed', 'undelivered', 'canceled', 'busy', 'no-answer'}

    project = models.ForeignKey(
        'ProjectManager.Project',
        on_delete=models.CASCADE,
        related_name='marketing_messages',
    )
    contact = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='messages',
    )
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='messages',
    )
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES, default=Campaign.CHANNEL_SMS)
    body = models.TextField(blank=True, default='')
    from_number = models.CharField(max_length=20, blank=True, default='')
    to_number = models.CharField(max_length=20, blank=True, default='')
    twilio_sid = models.CharField(max_length=64, blank=True, default='', db_index=True)
    status = models.CharField(max_length=32, default='queued')
    error_code = models.CharField(max_length=20, blank=True, default='')
    error_message = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', '-created_at']),
            models.Index(fields=['project', 'direction']),
        ]

    def __str__(self):
        return f"{self.get_direction_display()} {self.channel} to {self.to_number} [{self.status}]"


class AdConnection(models.Model):
    """
    A project's link to one advertising platform (Google Ads or Meta Ads).

    Credentials differ per provider, so they live in an encrypted JSON blob
    (`credentials` property) rather than one column per secret:
      - meta:   {"access_token": ...}
      - google: {"developer_token": ..., "client_id": ..., "client_secret": ...,
                 "refresh_token": ..., "login_customer_id": ...(optional)}
    `account_id` is the Meta ad account ID / Google Ads customer ID
    (digits only, no "act_" prefix or dashes).
    """

    PROVIDER_GOOGLE = 'google'
    PROVIDER_META = 'meta'
    PROVIDER_CHOICES = [
        (PROVIDER_GOOGLE, 'Google Ads'),
        (PROVIDER_META, 'Meta Ads'),
    ]

    # Credential keys each provider requires before we can call its API.
    REQUIRED_CREDENTIALS = {
        PROVIDER_GOOGLE: ('developer_token', 'client_id', 'client_secret', 'refresh_token'),
        PROVIDER_META: ('access_token',),
    }

    project = models.ForeignKey(
        'ProjectManager.Project',
        on_delete=models.CASCADE,
        related_name='ad_connections',
    )
    provider = models.CharField(max_length=10, choices=PROVIDER_CHOICES)
    credentials_encrypted = models.TextField(blank=True, default='')
    account_id = models.CharField(
        max_length=32,
        blank=True,
        default='',
        help_text='Meta ad account ID or Google Ads customer ID, digits only',
    )
    account_name = models.CharField(max_length=255, blank=True, default='')
    currency = models.CharField(max_length=8, blank=True, default='')
    last_verified_at = models.DateTimeField(null=True, blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'provider'],
                name='unique_ad_connection_provider_per_project',
            )
        ]

    def __str__(self):
        return f"{self.get_provider_display()} connection for {self.project.name}"

    @property
    def credentials(self) -> dict:
        raw = decrypt_secret(self.credentials_encrypted)
        if not raw:
            return {}
        try:
            data = json.loads(raw)
        except ValueError:
            return {}
        return data if isinstance(data, dict) else {}

    @credentials.setter
    def credentials(self, value: dict):
        value = {k: v for k, v in (value or {}).items() if v}
        self.credentials_encrypted = encrypt_secret(json.dumps(value)) if value else ''

    @property
    def is_configured(self) -> bool:
        """True when every required credential and the account ID are present."""
        if not self.account_id:
            return False
        stored = self.credentials
        return all(stored.get(key) for key in self.REQUIRED_CREDENTIALS[self.provider])


class AdCampaign(models.Model):
    """
    A locally mirrored ad campaign from a connected platform.

    Rows are created and refreshed by AdsService.sync(): campaign metadata
    plus lifetime performance totals. `status` is normalized across providers
    for filtering and badges; `provider_status` keeps the platform's raw value.
    """

    STATUS_ACTIVE = 'active'
    STATUS_PAUSED = 'paused'
    STATUS_ENDED = 'ended'
    STATUS_OTHER = 'other'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_PAUSED, 'Paused'),
        (STATUS_ENDED, 'Ended'),
        (STATUS_OTHER, 'Other'),
    ]

    project = models.ForeignKey(
        'ProjectManager.Project',
        on_delete=models.CASCADE,
        related_name='ad_campaigns',
    )
    provider = models.CharField(max_length=10, choices=AdConnection.PROVIDER_CHOICES)
    external_id = models.CharField(max_length=64)
    account_id = models.CharField(max_length=32, blank=True, default='')
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_OTHER)
    provider_status = models.CharField(max_length=50, blank=True, default='')
    objective = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text='Meta objective or Google advertising channel type',
    )
    daily_budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=8, blank=True, default='')
    impressions = models.BigIntegerField(default=0)
    clicks = models.BigIntegerField(default=0)
    spend = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    conversions = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-spend', '-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'provider', 'external_id'],
                name='unique_ad_campaign_per_project_provider',
            )
        ]
        indexes = [
            models.Index(fields=['project', 'status']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_provider_display()}) [{self.get_status_display()}]"

    @property
    def manager_url(self) -> str:
        """Deep link to the campaign in the platform's own ads manager."""
        if self.provider == AdConnection.PROVIDER_META:
            base = 'https://adsmanager.facebook.com/adsmanager/manage/campaigns'
            if self.account_id:
                return f'{base}?act={self.account_id}&selected_campaign_ids={self.external_id}'
            return base
        return 'https://ads.google.com/aw/campaigns'
