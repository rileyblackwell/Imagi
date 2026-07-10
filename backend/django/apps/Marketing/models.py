"""
Models for the Marketing app.

Everything here is scoped to a ProjectManager Project: each user project
(business) gets its own Twilio configuration, audience of contacts, campaigns,
and message history. Twilio is the delivery layer — SMS/MMS campaigns and
two-way texting via Programmable Messaging, voice broadcasts via
Programmable Voice.
"""

import base64
import hashlib
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
