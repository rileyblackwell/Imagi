"""
Serializers for the Marketing app API.
"""

import re

from rest_framework import serializers

from ..models import Campaign, Contact, MarketingSettings, Message
from ..services.campaign_service import inbound_webhook_url, status_callback_url

# Twilio hard limit for a single (concatenated) SMS body.
SMS_MAX_LENGTH = 1600

ACCOUNT_SID_PATTERN = re.compile(r'^AC[0-9a-fA-F]{32}$')
MESSAGING_SERVICE_SID_PATTERN = re.compile(r'^MG[0-9a-fA-F]{32}$')


class TagsField(serializers.ListField):
    """A list of short, non-empty tag strings, trimmed and de-duplicated."""

    child = serializers.CharField(max_length=50)

    def to_internal_value(self, data):
        tags = super().to_internal_value(data)
        cleaned = []
        seen = set()
        for tag in tags:
            tag = tag.strip()
            if not tag or tag.lower() in seen:
                continue
            seen.add(tag.lower())
            cleaned.append(tag)
        return cleaned


class MarketingSettingsSerializer(serializers.ModelSerializer):
    # The auth token is write-only: clients send it once, then only see whether
    # one is stored. It never leaves the server after that.
    twilio_auth_token = serializers.CharField(
        write_only=True, required=False, allow_blank=True, trim_whitespace=True
    )
    twilio_auth_token_set = serializers.SerializerMethodField()
    is_configured = serializers.BooleanField(read_only=True)
    status_callback_url = serializers.SerializerMethodField()
    inbound_webhook_url = serializers.SerializerMethodField()

    class Meta:
        model = MarketingSettings
        fields = [
            'twilio_account_sid',
            'twilio_auth_token',
            'twilio_auth_token_set',
            'twilio_phone_number',
            'twilio_messaging_service_sid',
            'voice',
            'account_friendly_name',
            'last_verified_at',
            'is_configured',
            'status_callback_url',
            'inbound_webhook_url',
        ]
        read_only_fields = ['account_friendly_name', 'last_verified_at']
        extra_kwargs = {
            'twilio_account_sid': {'required': False, 'allow_blank': True},
            'twilio_phone_number': {'required': False, 'allow_blank': True},
            'twilio_messaging_service_sid': {'required': False, 'allow_blank': True},
            'voice': {'required': False},
        }

    def get_twilio_auth_token_set(self, obj) -> bool:
        return bool(obj.twilio_auth_token_encrypted)

    def get_status_callback_url(self, obj) -> str:
        return status_callback_url(obj.project_id)

    def get_inbound_webhook_url(self, obj) -> str:
        return inbound_webhook_url(obj.project_id)

    def validate_twilio_account_sid(self, value):
        value = value.strip()
        if value and not ACCOUNT_SID_PATTERN.match(value):
            raise serializers.ValidationError(
                'Account SID should look like "AC" followed by 32 hex characters.'
            )
        return value

    def validate_twilio_messaging_service_sid(self, value):
        value = value.strip()
        if value and not MESSAGING_SERVICE_SID_PATTERN.match(value):
            raise serializers.ValidationError(
                'Messaging Service SID should look like "MG" followed by 32 hex characters.'
            )
        return value

    def update(self, instance, validated_data):
        # An omitted or blank token means "keep the stored one"; disconnecting
        # the account (clearing the SID) also wipes the stored token.
        auth_token = validated_data.pop('twilio_auth_token', '')
        instance = super().update(instance, validated_data)
        if auth_token:
            instance.twilio_auth_token = auth_token
            instance.save(update_fields=['twilio_auth_token_encrypted', 'updated_at'])
        elif not instance.twilio_account_sid and instance.twilio_auth_token_encrypted:
            instance.twilio_auth_token_encrypted = ''
            instance.save(update_fields=['twilio_auth_token_encrypted', 'updated_at'])
        return instance


class ContactSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(read_only=True)
    tags = TagsField(required=False)

    class Meta:
        model = Contact
        fields = [
            'id', 'first_name', 'last_name', 'display_name', 'phone_number',
            'email', 'tags', 'consent', 'source', 'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['source', 'created_at', 'updated_at']

    def validate_phone_number(self, value):
        value = value.strip().replace(' ', '')
        project = self.context['project']
        duplicates = Contact.objects.filter(project=project, phone_number=value)
        if self.instance:
            duplicates = duplicates.exclude(id=self.instance.id)
        if duplicates.exists():
            raise serializers.ValidationError('A contact with this phone number already exists.')
        return value

    def create(self, validated_data):
        validated_data['project'] = self.context['project']
        return super().create(validated_data)


class CampaignSerializer(serializers.ModelSerializer):
    audience_tags = TagsField(required=False)
    stats = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = [
            'id', 'name', 'channel', 'body', 'audience_type', 'audience_tags',
            'status', 'scheduled_at', 'started_at', 'completed_at',
            'created_at', 'updated_at', 'stats',
        ]
        read_only_fields = ['status', 'scheduled_at', 'started_at', 'completed_at',
                            'created_at', 'updated_at']

    def get_stats(self, obj) -> dict:
        # Prefer counts annotated by the view; fall back to querying (detail view).
        total = getattr(obj, 'message_total', None)
        if total is None:
            messages = obj.messages.all()
            total = messages.count()
            delivered = messages.filter(status__in=Message.DELIVERED_STATUSES).count()
            failed = messages.filter(status__in=Message.FAILED_STATUSES).count()
        else:
            delivered = obj.message_delivered or 0
            failed = obj.message_failed or 0
        return {
            'recipients': total,
            'delivered': delivered,
            'failed': failed,
            'pending': max(total - delivered - failed, 0),
        }

    def validate(self, attrs):
        channel = attrs.get('channel', getattr(self.instance, 'channel', Campaign.CHANNEL_SMS))
        body = attrs.get('body', getattr(self.instance, 'body', ''))
        if channel == Campaign.CHANNEL_SMS and len(body) > SMS_MAX_LENGTH:
            raise serializers.ValidationError(
                {'body': f'SMS messages are limited to {SMS_MAX_LENGTH} characters.'}
            )
        audience_type = attrs.get(
            'audience_type', getattr(self.instance, 'audience_type', Campaign.AUDIENCE_ALL)
        )
        audience_tags = attrs.get(
            'audience_tags', getattr(self.instance, 'audience_tags', [])
        )
        if audience_type == Campaign.AUDIENCE_TAGS and not audience_tags:
            raise serializers.ValidationError(
                {'audience_tags': 'Pick at least one tag, or target all subscribed contacts.'}
            )
        return attrs

    def create(self, validated_data):
        validated_data['project'] = self.context['project']
        return super().create(validated_data)


class MessageSerializer(serializers.ModelSerializer):
    contact_id = serializers.IntegerField(read_only=True)
    contact_name = serializers.SerializerMethodField()
    campaign_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Message
        fields = [
            'id', 'direction', 'channel', 'body', 'from_number', 'to_number',
            'status', 'error_code', 'error_message', 'contact_id', 'contact_name',
            'campaign_id', 'created_at',
        ]

    def get_contact_name(self, obj) -> str:
        return obj.contact.display_name if obj.contact else obj.from_number


class ConversationSerializer(serializers.ModelSerializer):
    """A contact plus their latest message — one inbox row."""

    display_name = serializers.CharField(read_only=True)
    last_message_body = serializers.CharField(read_only=True, default='')
    last_message_direction = serializers.CharField(read_only=True, default='')
    last_message_at = serializers.DateTimeField(read_only=True, default=None)
    message_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Contact
        fields = [
            'id', 'display_name', 'phone_number', 'consent',
            'last_message_body', 'last_message_direction', 'last_message_at',
            'message_count',
        ]
