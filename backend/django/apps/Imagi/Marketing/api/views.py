"""
API views for the Marketing app.

Everything except the Twilio webhooks is scoped to a project owned by the
authenticated user: /api/v1/marketing/projects/<project_id>/...

The webhook endpoints authenticate requests with Twilio's X-Twilio-Signature
header instead of a user session, since they're called by Twilio itself.
"""

import datetime
import logging

from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Count, Max, OuterRef, Q, Subquery
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.Imagi.Build.ProjectManager.models import Project

from ..models import Campaign, Contact, MarketingSettings, Message, phone_validator
from ..services.campaign_service import (
    CampaignService,
    CampaignServiceError,
    webhook_base_url,
)
from ..services.twilio_client import validate_webhook_signature
from .serializers import (
    CampaignSerializer,
    ContactSerializer,
    ConversationSerializer,
    MarketingSettingsSerializer,
    MessageSerializer,
)

logger = logging.getLogger(__name__)

IMPORT_MAX_ROWS = 1000
THREAD_MESSAGE_LIMIT = 100
CAMPAIGN_MESSAGE_LIMIT = 500


def paginate(request, queryset, default_limit=50, max_limit=200):
    """Slice a queryset by ?limit=&offset= and return (page, total)."""
    try:
        limit = int(request.query_params.get('limit', default_limit))
    except (TypeError, ValueError):
        limit = default_limit
    limit = max(1, min(limit, max_limit))
    try:
        offset = max(int(request.query_params.get('offset', 0)), 0)
    except (TypeError, ValueError):
        offset = 0
    return queryset[offset:offset + limit], queryset.count()


def campaigns_with_stats(project):
    """Campaign queryset annotated with the counts CampaignSerializer reads."""
    return project.marketing_campaigns.annotate(
        message_total=Count('messages'),
        message_delivered=Count(
            'messages', filter=Q(messages__status__in=Message.DELIVERED_STATUSES)
        ),
        message_failed=Count(
            'messages', filter=Q(messages__status__in=Message.FAILED_STATUSES)
        ),
    )


class ProjectScopedView(APIView):
    """Base view resolving the project from the URL and enforcing ownership."""

    permission_classes = [IsAuthenticated]

    def get_project(self) -> Project:
        try:
            return Project.objects.get(
                id=self.kwargs['project_id'],
                user=self.request.user,
                is_active=True,
            )
        except Project.DoesNotExist:
            raise NotFound('Project not found')

    def get_settings(self, project) -> MarketingSettings:
        settings_obj, _ = MarketingSettings.objects.get_or_create(project=project)
        return settings_obj


# -- Settings ------------------------------------------------------------------


class MarketingSettingsView(ProjectScopedView):
    """Read or update the project's Twilio configuration."""

    def get(self, request, project_id):
        settings_obj = self.get_settings(self.get_project())
        return Response({'settings': MarketingSettingsSerializer(settings_obj).data})

    def put(self, request, project_id):
        settings_obj = self.get_settings(self.get_project())
        serializer = MarketingSettingsSerializer(settings_obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'settings': MarketingSettingsSerializer(settings_obj).data})


class VerifyConnectionView(ProjectScopedView):
    """Test the stored Twilio credentials by fetching the account."""

    def post(self, request, project_id):
        project = self.get_project()
        self.get_settings(project)
        try:
            result = CampaignService(project).verify()
        except CampaignServiceError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        settings_obj = MarketingSettings.objects.get(project=project)
        return Response({
            'verified': True,
            **result,
            'settings': MarketingSettingsSerializer(settings_obj).data,
        })


# -- Overview --------------------------------------------------------------------


class OverviewView(ProjectScopedView):
    """Dashboard stats for the marketing workspace."""

    def get(self, request, project_id):
        project = self.get_project()
        settings_obj = MarketingSettings.objects.filter(project=project).first()
        contacts = project.marketing_contacts.all()
        campaigns = project.marketing_campaigns.all()
        messages = project.marketing_messages.all()
        since = timezone.now() - datetime.timedelta(days=30)
        outbound = messages.filter(direction=Message.DIRECTION_OUTBOUND, created_at__gte=since)

        recent_campaigns = campaigns_with_stats(project)[:5]
        recent_inbound = (
            messages.filter(direction=Message.DIRECTION_INBOUND)
            .select_related('contact')[:5]
        )

        return Response({
            'stats': {
                'configured': bool(settings_obj and settings_obj.is_configured),
                'contacts_total': contacts.count(),
                'contacts_subscribed': contacts.filter(consent=Contact.CONSENT_SUBSCRIBED).count(),
                'campaigns_total': campaigns.count(),
                'campaigns_active': campaigns.filter(
                    status__in=[Campaign.STATUS_SCHEDULED, Campaign.STATUS_SENDING]
                ).count(),
                'messages_sent_30d': outbound.count(),
                'messages_delivered_30d': outbound.filter(
                    status__in=Message.DELIVERED_STATUSES
                ).count(),
                'messages_failed_30d': outbound.filter(
                    status__in=Message.FAILED_STATUSES
                ).count(),
                'replies_30d': messages.filter(
                    direction=Message.DIRECTION_INBOUND, created_at__gte=since
                ).count(),
            },
            'recent_campaigns': CampaignSerializer(recent_campaigns, many=True).data,
            'recent_inbound': MessageSerializer(recent_inbound, many=True).data,
        })


# -- Contacts ---------------------------------------------------------------------


class ContactListCreateView(ProjectScopedView):
    """List/search the audience, or add a contact."""

    def get(self, request, project_id):
        project = self.get_project()
        contacts = project.marketing_contacts.all()

        search = request.query_params.get('search', '').strip()
        if search:
            contacts = contacts.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(phone_number__icontains=search)
                | Q(email__icontains=search)
            )
        consent = request.query_params.get('consent', '').strip()
        if consent in (Contact.CONSENT_SUBSCRIBED, Contact.CONSENT_UNSUBSCRIBED):
            contacts = contacts.filter(consent=consent)
        tag = request.query_params.get('tag', '').strip().lower()
        if tag:
            # JSONField "contains" isn't available on SQLite; match in Python.
            matching_ids = [c.id for c in contacts if tag in c.tag_set()]
            contacts = contacts.filter(id__in=matching_ids)

        page, total = paginate(request, contacts)
        return Response({
            'contacts': ContactSerializer(page, many=True).data,
            'total': total,
        })

    def post(self, request, project_id):
        project = self.get_project()
        serializer = ContactSerializer(data=request.data, context={'project': project})
        serializer.is_valid(raise_exception=True)
        contact = serializer.save()
        return Response(
            {'contact': ContactSerializer(contact).data},
            status=status.HTTP_201_CREATED,
        )


class ContactDetailView(ProjectScopedView):
    """Read, update, or remove a single contact."""

    def get_contact(self, project, pk) -> Contact:
        try:
            return project.marketing_contacts.get(id=pk)
        except Contact.DoesNotExist:
            raise NotFound('Contact not found')

    def get(self, request, project_id, pk):
        contact = self.get_contact(self.get_project(), pk)
        return Response({'contact': ContactSerializer(contact).data})

    def patch(self, request, project_id, pk):
        project = self.get_project()
        contact = self.get_contact(project, pk)
        serializer = ContactSerializer(
            contact, data=request.data, partial=True, context={'project': project}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'contact': ContactSerializer(contact).data})

    def delete(self, request, project_id, pk):
        contact = self.get_contact(self.get_project(), pk)
        contact.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ContactImportView(ProjectScopedView):
    """
    Bulk-import contacts. Accepts {"contacts": [{first_name, last_name,
    phone_number, email, tags}, ...]}; invalid or duplicate rows are skipped
    and reported rather than failing the whole import.
    """

    def post(self, request, project_id):
        project = self.get_project()
        rows = request.data.get('contacts')
        if not isinstance(rows, list) or not rows:
            return Response(
                {'error': 'Provide a non-empty "contacts" list.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(rows) > IMPORT_MAX_ROWS:
            return Response(
                {'error': f'Imports are limited to {IMPORT_MAX_ROWS} contacts at a time.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        existing_phones = set(
            project.marketing_contacts.values_list('phone_number', flat=True)
        )
        created = []
        skipped = []
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                skipped.append({'index': index, 'reason': 'Row is not an object'})
                continue
            phone = str(row.get('phone_number', '')).strip().replace(' ', '')
            try:
                phone_validator(phone)
            except DjangoValidationError:
                skipped.append({
                    'index': index,
                    'phone_number': phone,
                    'reason': 'Invalid phone number (must be E.164, e.g. +15551234567)',
                })
                continue
            if phone in existing_phones:
                skipped.append({
                    'index': index,
                    'phone_number': phone,
                    'reason': 'Duplicate phone number',
                })
                continue

            email = str(row.get('email', '') or '').strip()
            if email:
                try:
                    validate_email(email)
                except DjangoValidationError:
                    email = ''
            tags = row.get('tags', [])
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(',')]
            if not isinstance(tags, list):
                tags = []
            tags = [str(t).strip()[:50] for t in tags if str(t).strip()][:20]

            created.append(Contact(
                project=project,
                first_name=str(row.get('first_name', '') or '').strip()[:100],
                last_name=str(row.get('last_name', '') or '').strip()[:100],
                phone_number=phone,
                email=email,
                tags=tags,
                source='import',
            ))
            existing_phones.add(phone)

        Contact.objects.bulk_create(created)
        return Response({
            'created': len(created),
            'skipped': skipped,
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class TagListView(ProjectScopedView):
    """Distinct tags across the project's audience, with contact counts."""

    def get(self, request, project_id):
        project = self.get_project()
        counts = {}
        display = {}
        for contact_tags in project.marketing_contacts.values_list('tags', flat=True):
            for tag in contact_tags or []:
                tag = str(tag).strip()
                if not tag:
                    continue
                key = tag.lower()
                counts[key] = counts.get(key, 0) + 1
                display.setdefault(key, tag)
        tags = [
            {'tag': display[key], 'count': counts[key]}
            for key in sorted(counts)
        ]
        return Response({'tags': tags})


# -- Inbox / conversations -----------------------------------------------------------


class ConversationListView(ProjectScopedView):
    """Contacts that have message history, newest activity first."""

    def get(self, request, project_id):
        project = self.get_project()
        last_message = Message.objects.filter(contact=OuterRef('pk')).order_by('-created_at')
        conversations = (
            project.marketing_contacts
            .annotate(
                last_message_at=Max('messages__created_at'),
                message_count=Count('messages'),
                last_message_body=Subquery(last_message.values('body')[:1]),
                last_message_direction=Subquery(last_message.values('direction')[:1]),
            )
            .filter(message_count__gt=0)
            .order_by('-last_message_at')
        )
        page, total = paginate(request, conversations, default_limit=100)
        return Response({
            'conversations': ConversationSerializer(page, many=True).data,
            'total': total,
        })


class ContactMessagesView(ProjectScopedView):
    """A contact's message thread (GET) and direct replies (POST)."""

    def get_contact(self, project, pk) -> Contact:
        try:
            return project.marketing_contacts.get(id=pk)
        except Contact.DoesNotExist:
            raise NotFound('Contact not found')

    def get(self, request, project_id, pk):
        project = self.get_project()
        contact = self.get_contact(project, pk)
        messages = contact.messages.order_by('-created_at')[:THREAD_MESSAGE_LIMIT]
        return Response({
            'contact': ContactSerializer(contact).data,
            'messages': MessageSerializer(messages, many=True).data,
        })

    def post(self, request, project_id, pk):
        project = self.get_project()
        contact = self.get_contact(project, pk)
        body = str(request.data.get('body', '') or '').strip()
        if not body:
            return Response({'error': 'Message body is required.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if len(body) > 1600:
            return Response({'error': 'SMS messages are limited to 1600 characters.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if contact.consent != Contact.CONSENT_SUBSCRIBED:
            return Response({'error': 'This contact has unsubscribed from messages.'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            message = CampaignService(project).send_direct(contact, body)
        except CampaignServiceError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {'message': MessageSerializer(message).data},
            status=status.HTTP_201_CREATED,
        )


# -- Campaigns -------------------------------------------------------------------------


class CampaignListCreateView(ProjectScopedView):
    """List campaigns with delivery stats, or create a draft."""

    def get(self, request, project_id):
        project = self.get_project()
        campaigns = campaigns_with_stats(project)
        status_filter = request.query_params.get('status', '').strip()
        if status_filter:
            campaigns = campaigns.filter(status=status_filter)
        page, total = paginate(request, campaigns)
        return Response({
            'campaigns': CampaignSerializer(page, many=True).data,
            'total': total,
        })

    def post(self, request, project_id):
        project = self.get_project()
        serializer = CampaignSerializer(data=request.data, context={'project': project})
        serializer.is_valid(raise_exception=True)
        campaign = serializer.save()
        return Response(
            {'campaign': CampaignSerializer(campaign).data},
            status=status.HTTP_201_CREATED,
        )


class CampaignDetailView(ProjectScopedView):
    """Campaign detail with per-recipient results; edit/delete drafts."""

    def get_campaign(self, project, pk, with_stats=False) -> Campaign:
        queryset = campaigns_with_stats(project) if with_stats else project.marketing_campaigns
        try:
            return queryset.get(id=pk)
        except Campaign.DoesNotExist:
            raise NotFound('Campaign not found')

    def get(self, request, project_id, pk):
        project = self.get_project()
        campaign = self.get_campaign(project, pk, with_stats=True)
        messages = campaign.messages.select_related('contact')[:CAMPAIGN_MESSAGE_LIMIT]
        return Response({
            'campaign': CampaignSerializer(campaign).data,
            'messages': MessageSerializer(messages, many=True).data,
        })

    def patch(self, request, project_id, pk):
        project = self.get_project()
        campaign = self.get_campaign(project, pk)
        if not campaign.is_editable:
            return Response(
                {'error': 'Only draft campaigns can be edited.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = CampaignSerializer(
            campaign, data=request.data, partial=True, context={'project': project}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'campaign': CampaignSerializer(campaign).data})

    def delete(self, request, project_id, pk):
        campaign = self.get_campaign(self.get_project(), pk)
        if campaign.status in (Campaign.STATUS_SENDING, Campaign.STATUS_SCHEDULED):
            return Response(
                {'error': 'Cancel this campaign before deleting it.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        campaign.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CampaignRecipientsPreviewView(ProjectScopedView):
    """How many contacts the campaign's audience currently resolves to."""

    def get(self, request, project_id, pk):
        project = self.get_project()
        try:
            campaign = project.marketing_campaigns.get(id=pk)
        except Campaign.DoesNotExist:
            raise NotFound('Campaign not found')
        count = CampaignService(project).recipients(campaign).count()
        return Response({'recipients': count})


class CampaignSendView(ProjectScopedView):
    """Send a draft campaign now, or schedule it via Twilio with send_at."""

    def post(self, request, project_id, pk):
        project = self.get_project()
        try:
            campaign = project.marketing_campaigns.get(id=pk)
        except Campaign.DoesNotExist:
            raise NotFound('Campaign not found')

        send_at = None
        raw_send_at = request.data.get('send_at')
        if raw_send_at:
            send_at = parse_datetime(str(raw_send_at))
            if send_at is None or timezone.is_naive(send_at):
                return Response(
                    {'error': 'send_at must be an ISO 8601 datetime with a timezone.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            result = CampaignService(project).send(campaign, send_at=send_at)
        except CampaignServiceError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        campaign = campaigns_with_stats(project).get(id=campaign.id)
        return Response({
            **result,
            'campaign': CampaignSerializer(campaign).data,
        })


class CampaignCancelView(ProjectScopedView):
    """Cancel a scheduled campaign before Twilio delivers it."""

    def post(self, request, project_id, pk):
        project = self.get_project()
        try:
            campaign = project.marketing_campaigns.get(id=pk)
        except Campaign.DoesNotExist:
            raise NotFound('Campaign not found')
        try:
            result = CampaignService(project).cancel(campaign)
        except CampaignServiceError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        campaign = campaigns_with_stats(project).get(id=campaign.id)
        return Response({**result, 'campaign': CampaignSerializer(campaign).data})


class CampaignSyncView(ProjectScopedView):
    """Refresh delivery statuses from Twilio (fallback when webhooks can't reach us)."""

    def post(self, request, project_id, pk):
        project = self.get_project()
        try:
            campaign = project.marketing_campaigns.get(id=pk)
        except Campaign.DoesNotExist:
            raise NotFound('Campaign not found')
        try:
            result = CampaignService(project).sync_statuses(campaign)
        except CampaignServiceError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        campaign = campaigns_with_stats(project).get(id=campaign.id)
        return Response({**result, 'campaign': CampaignSerializer(campaign).data})


# -- Twilio webhooks ---------------------------------------------------------------------


class TwilioWebhookView(APIView):
    """
    Base for endpoints Twilio calls directly. There's no user session;
    authenticity comes from validating the X-Twilio-Signature header with the
    project's stored auth token.
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    def get_webhook_project(self, project_id) -> Project:
        try:
            return Project.objects.get(id=project_id, is_active=True)
        except Project.DoesNotExist:
            raise NotFound('Unknown project')

    def extract_params(self, request) -> dict:
        data = request.data
        return data.dict() if hasattr(data, 'dict') else dict(data)

    def is_authentic(self, request, project, params) -> bool:
        config = MarketingSettings.objects.filter(project=project).first()
        token = config.twilio_auth_token if config else ''
        if not token:
            return False
        signature = request.headers.get('X-Twilio-Signature', '')
        base = webhook_base_url()
        # Twilio signs the exact public URL it called. Prefer the configured
        # base (stable behind proxies), fall back to what Django reconstructs.
        url = f'{base}{request.path}' if base else request.build_absolute_uri()
        return validate_webhook_signature(token, url, params, signature)


class TwilioStatusWebhookView(TwilioWebhookView):
    """Delivery status callbacks for messages and calls."""

    def post(self, request, project_id):
        project = self.get_webhook_project(project_id)
        params = self.extract_params(request)
        if not self.is_authentic(request, project, params):
            logger.warning(f'Rejected unsigned Twilio status callback for project {project_id}')
            return Response(status=status.HTTP_403_FORBIDDEN)
        CampaignService(project).apply_status_update(params)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TwilioInboundWebhookView(TwilioWebhookView):
    """Incoming SMS: log the message, keep consent in sync, reply with empty TwiML."""

    def post(self, request, project_id):
        project = self.get_webhook_project(project_id)
        params = self.extract_params(request)
        if not self.is_authentic(request, project, params):
            logger.warning(f'Rejected unsigned Twilio inbound webhook for project {project_id}')
            return Response(status=status.HTTP_403_FORBIDDEN)
        CampaignService(project).record_inbound(params)
        return HttpResponse(
            '<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
            content_type='text/xml',
        )
