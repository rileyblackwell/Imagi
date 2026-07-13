"""
Ad platform workflows for the Marketing app.

Wraps the raw Google Ads / Meta Ads clients with everything project-specific:
saving and verifying connections, mirroring campaigns + lifetime performance
into AdCampaign rows, and pushing pause/resume back to the platform.

Ads are managed in the platforms' own managers (creating campaigns needs
their full creative flows); Imagi is the unified dashboard and remote control.
"""

import logging
from decimal import Decimal, InvalidOperation

from django.db.models import Count, Q, Sum
from django.utils import timezone

from ..models import AdCampaign, AdConnection
from .google_ads_client import GoogleAdsClient, GoogleAdsError
from .meta_ads_client import MetaAdsClient, MetaAdsError, extract_conversions

logger = logging.getLogger(__name__)


class AdsServiceError(Exception):
    """A user-facing problem (bad credentials, platform rejection, no connection)."""


def _decimal(value, divisor=1):
    """Parse a platform number (often a string) into a Decimal, or None."""
    if value in (None, ''):
        return None
    try:
        return Decimal(str(value)) / divisor
    except (InvalidOperation, ValueError):
        return None


def _int(value) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


# Provider status → our normalized status. Anything unlisted becomes "other"
# (Meta's IN_PROCESS / WITH_ISSUES, Google's UNKNOWN, ...).
META_STATUS_MAP = {
    'ACTIVE': AdCampaign.STATUS_ACTIVE,
    'PAUSED': AdCampaign.STATUS_PAUSED,
    'CAMPAIGN_PAUSED': AdCampaign.STATUS_PAUSED,
    'ADSET_PAUSED': AdCampaign.STATUS_PAUSED,
    'ARCHIVED': AdCampaign.STATUS_ENDED,
    'DELETED': AdCampaign.STATUS_ENDED,
    'COMPLETED': AdCampaign.STATUS_ENDED,
}
GOOGLE_STATUS_MAP = {
    'ENABLED': AdCampaign.STATUS_ACTIVE,
    'PAUSED': AdCampaign.STATUS_PAUSED,
    'REMOVED': AdCampaign.STATUS_ENDED,
}


class AdsService:
    """Ad platform operations for a single project."""

    def __init__(self, project):
        self.project = project

    # -- connections -----------------------------------------------------------

    def get_connection(self, provider: str) -> AdConnection:
        connection, _ = AdConnection.objects.get_or_create(
            project=self.project, provider=provider
        )
        return connection

    def save_credentials(self, provider: str, account_id: str, credentials: dict) -> AdConnection:
        """
        Store the account ID and merge in the provided credential values.
        Blank credential values mean "keep what's stored" so users can update
        one field without re-entering the rest.
        """
        connection = self.get_connection(provider)
        merged = connection.credentials
        for key, value in (credentials or {}).items():
            value = str(value or '').strip()
            if value:
                merged[key] = value

        account_id = str(account_id or '').strip()
        if provider == AdConnection.PROVIDER_META:
            account_id = account_id.removeprefix('act_')
        account_id = account_id.replace('-', '')

        connection.credentials = merged
        connection.account_id = account_id
        if not account_id and not merged:
            # Fully cleared — treat as a disconnect.
            connection.account_name = ''
            connection.currency = ''
            connection.last_verified_at = None
        connection.save()
        return connection

    def disconnect(self, provider: str) -> None:
        """Drop the connection and its mirrored campaigns."""
        AdConnection.objects.filter(project=self.project, provider=provider).delete()
        AdCampaign.objects.filter(project=self.project, provider=provider).delete()

    def _client(self, connection: AdConnection):
        if not connection.is_configured:
            raise AdsServiceError(
                f'{connection.get_provider_display()} is not connected. Add the '
                'account ID and API credentials in Marketing settings first.'
            )
        creds = connection.credentials
        try:
            if connection.provider == AdConnection.PROVIDER_META:
                return MetaAdsClient(creds.get('access_token', ''), connection.account_id)
            return GoogleAdsClient(
                developer_token=creds.get('developer_token', ''),
                client_id=creds.get('client_id', ''),
                client_secret=creds.get('client_secret', ''),
                refresh_token=creds.get('refresh_token', ''),
                customer_id=connection.account_id,
                login_customer_id=creds.get('login_customer_id', ''),
            )
        except (MetaAdsError, GoogleAdsError) as exc:
            raise AdsServiceError(str(exc)) from exc

    def verify(self, provider: str) -> AdConnection:
        """Check the stored credentials against the platform and cache the account info."""
        connection = self.get_connection(provider)
        client = self._client(connection)
        try:
            if provider == AdConnection.PROVIDER_META:
                account = client.fetch_ad_account()
                connection.account_name = account.get('name', '')
                connection.currency = account.get('currency', '')
            else:
                customer = client.fetch_customer()
                connection.account_name = customer.get('name', '')
                connection.currency = customer.get('currency', '')
        except (MetaAdsError, GoogleAdsError) as exc:
            raise AdsServiceError(
                f'{connection.get_provider_display()} rejected the credentials: {exc}'
            ) from exc

        connection.last_verified_at = timezone.now()
        connection.save(update_fields=['account_name', 'currency', 'last_verified_at', 'updated_at'])
        return connection

    # -- syncing ----------------------------------------------------------------

    def sync(self, provider: str) -> dict:
        """
        Mirror the platform's campaigns into AdCampaign rows: upsert everything
        returned and drop local rows the platform no longer reports.
        """
        connection = self.get_connection(provider)
        client = self._client(connection)
        try:
            raw_campaigns = client.list_campaigns()
        except (MetaAdsError, GoogleAdsError) as exc:
            raise AdsServiceError(
                f'Could not fetch campaigns from {connection.get_provider_display()}: {exc}'
            ) from exc

        now = timezone.now()
        seen_ids = []
        for raw in raw_campaigns:
            if provider == AdConnection.PROVIDER_META:
                parsed = self._parse_meta_campaign(raw)
            else:
                parsed = self._parse_google_campaign(raw)
            if not parsed:
                continue
            external_id = parsed.pop('external_id')
            seen_ids.append(external_id)
            AdCampaign.objects.update_or_create(
                project=self.project,
                provider=provider,
                external_id=external_id,
                defaults={
                    **parsed,
                    'account_id': connection.account_id,
                    'currency': connection.currency,
                    'last_synced_at': now,
                },
            )

        removed, _ = (
            AdCampaign.objects
            .filter(project=self.project, provider=provider)
            .exclude(external_id__in=seen_ids)
            .delete()
        )

        connection.last_synced_at = now
        connection.save(update_fields=['last_synced_at', 'updated_at'])
        return {'synced': len(seen_ids), 'removed': removed}

    def sync_all(self) -> dict:
        """Sync every configured provider; collect per-provider errors instead of failing all."""
        results = {}
        errors = {}
        connections = AdConnection.objects.filter(project=self.project)
        configured = [c for c in connections if c.is_configured]
        if not configured:
            raise AdsServiceError(
                'No ad accounts are connected yet. Connect Google Ads or Meta Ads '
                'in Marketing settings first.'
            )
        for connection in configured:
            try:
                results[connection.provider] = self.sync(connection.provider)
            except AdsServiceError as exc:
                errors[connection.provider] = str(exc)
        return {'results': results, 'errors': errors}

    def _parse_meta_campaign(self, raw: dict):
        external_id = str(raw.get('id', '') or '')
        if not external_id:
            return None
        insights_rows = (raw.get('insights') or {}).get('data') or [{}]
        insights = insights_rows[0]
        effective_status = raw.get('effective_status') or raw.get('status') or ''
        return {
            'external_id': external_id,
            'name': raw.get('name', '') or external_id,
            'status': META_STATUS_MAP.get(effective_status, AdCampaign.STATUS_OTHER),
            'provider_status': effective_status,
            'objective': str(raw.get('objective', '') or ''),
            # Meta returns daily_budget in the account currency's minor units.
            'daily_budget': _decimal(raw.get('daily_budget'), divisor=100),
            'impressions': _int(insights.get('impressions')),
            'clicks': _int(insights.get('clicks')),
            'spend': _decimal(insights.get('spend')) or Decimal(0),
            'conversions': _decimal(extract_conversions(insights)),
        }

    def _parse_google_campaign(self, raw: dict):
        campaign = raw.get('campaign') or {}
        external_id = str(campaign.get('id', '') or '')
        if not external_id:
            return None
        metrics = raw.get('metrics') or {}
        budget = raw.get('campaignBudget') or {}
        status = campaign.get('status', '')
        return {
            'external_id': external_id,
            'name': campaign.get('name', '') or external_id,
            'status': GOOGLE_STATUS_MAP.get(status, AdCampaign.STATUS_OTHER),
            'provider_status': status,
            'objective': str(campaign.get('advertisingChannelType', '') or ''),
            'daily_budget': _decimal(budget.get('amountMicros'), divisor=1_000_000),
            'impressions': _int(metrics.get('impressions')),
            'clicks': _int(metrics.get('clicks')),
            'spend': _decimal(metrics.get('costMicros'), divisor=1_000_000) or Decimal(0),
            'conversions': _decimal(metrics.get('conversions')),
        }

    # -- campaign control ----------------------------------------------------------

    def set_campaign_active(self, campaign: AdCampaign, active: bool) -> AdCampaign:
        """Push pause/resume to the platform, then update the local mirror."""
        if campaign.status not in (AdCampaign.STATUS_ACTIVE, AdCampaign.STATUS_PAUSED):
            raise AdsServiceError('Only active or paused campaigns can be toggled.')
        connection = self.get_connection(campaign.provider)
        client = self._client(connection)
        try:
            client.set_campaign_status(campaign.external_id, active=active)
        except (MetaAdsError, GoogleAdsError) as exc:
            raise AdsServiceError(
                f'{connection.get_provider_display()} rejected the change: {exc}'
            ) from exc
        campaign.status = AdCampaign.STATUS_ACTIVE if active else AdCampaign.STATUS_PAUSED
        campaign.provider_status = ''
        campaign.last_synced_at = timezone.now()
        campaign.save(update_fields=['status', 'provider_status', 'last_synced_at', 'updated_at'])
        return campaign


def ads_summary(project) -> dict:
    """Aggregate ads stats for the overview dashboard and the ads tab header."""
    connections = list(AdConnection.objects.filter(project=project))
    connected = [c.provider for c in connections if c.is_configured]
    totals = AdCampaign.objects.filter(project=project).aggregate(
        campaigns_total=Count('id'),
        campaigns_active=Count('id', filter=Q(status=AdCampaign.STATUS_ACTIVE)),
        impressions=Sum('impressions'),
        clicks=Sum('clicks'),
        spend=Sum('spend'),
    )
    last_synced = [c.last_synced_at for c in connections if c.last_synced_at]
    currencies = {c.currency for c in connections if c.is_configured and c.currency}
    spend = (totals['spend'] or Decimal(0)).quantize(Decimal('0.01'))
    return {
        'connected_providers': connected,
        'campaigns_total': totals['campaigns_total'] or 0,
        'campaigns_active': totals['campaigns_active'] or 0,
        'impressions': totals['impressions'] or 0,
        'clicks': totals['clicks'] or 0,
        'spend': str(spend),
        'currency': currencies.pop() if len(currencies) == 1 else '',
        'last_synced_at': max(last_synced).isoformat() if last_synced else None,
    }
