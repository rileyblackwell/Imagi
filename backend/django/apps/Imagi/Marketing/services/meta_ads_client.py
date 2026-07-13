"""
Minimal Meta (Facebook/Instagram) Marketing API client for the Marketing app.

Talks to the Graph API directly with `requests`, mirroring twilio_client.py —
the ads dashboard only needs a handful of endpoints: verify the ad account,
list campaigns with lifetime insights, and pause/resume a campaign.

Auth is a user or system-user access token with the `ads_management` (or
`ads_read` for read-only) permission, created in Meta Business settings.

API reference: https://developers.facebook.com/docs/marketing-apis
"""

import logging

import requests

logger = logging.getLogger(__name__)

GRAPH_API_VERSION = 'v23.0'
API_BASE = f'https://graph.facebook.com/{GRAPH_API_VERSION}'
REQUEST_TIMEOUT = 20  # seconds

CAMPAIGN_FIELDS = (
    'id,name,status,effective_status,objective,daily_budget,'
    'insights.date_preset(maximum){impressions,clicks,spend,actions}'
)

# Insight action types we count as a "conversion" for the dashboard.
CONVERSION_ACTION_TYPES = {
    'purchase',
    'omni_purchase',
    'onsite_web_purchase',
    'lead',
    'onsite_web_lead',
    'complete_registration',
}


class MetaAdsError(Exception):
    """Raised when the Graph API can't be reached or returns an error."""

    def __init__(self, message, status=None, code=None):
        super().__init__(message)
        self.status = status
        self.code = code


class MetaAdsClient:
    def __init__(self, access_token: str, account_id: str):
        if not access_token or not account_id:
            raise MetaAdsError('Meta access token and ad account ID are required.')
        self.access_token = access_token
        # Normalize "act_1234" and "1234" to digits; API paths add the prefix.
        self.account_id = str(account_id).strip().removeprefix('act_')

    def _request(self, method: str, path: str, params=None, data=None) -> dict:
        url = f'{API_BASE}/{path.lstrip("/")}'
        params = dict(params or {})
        params['access_token'] = self.access_token
        try:
            response = requests.request(
                method, url,
                params=params,
                data=data,
                timeout=REQUEST_TIMEOUT,
            )
        except requests.RequestException as exc:
            logger.warning(f'Meta Ads request failed: {exc}')
            raise MetaAdsError(f'Could not reach the Meta API: {exc}') from exc

        try:
            payload = response.json()
        except ValueError:
            payload = {}

        if response.status_code >= 400 or 'error' in payload:
            error = payload.get('error') or {}
            message = error.get('error_user_msg') or error.get('message') \
                or f'Meta returned HTTP {response.status_code}'
            raise MetaAdsError(message, status=response.status_code, code=error.get('code'))
        return payload

    # -- Account --------------------------------------------------------------

    def fetch_ad_account(self) -> dict:
        """Fetch the ad account; used to verify the token and account ID."""
        return self._request(
            'GET', f'act_{self.account_id}',
            params={'fields': 'name,account_status,currency'},
        )

    # -- Campaigns --------------------------------------------------------------

    def list_campaigns(self) -> list:
        """
        Campaigns on the ad account with lifetime insights, following Graph
        API pagination.
        """
        campaigns = []
        params = {'fields': CAMPAIGN_FIELDS, 'limit': 100}
        path = f'act_{self.account_id}/campaigns'
        for _ in range(20):  # hard cap: 2000 campaigns
            payload = self._request('GET', path, params=params)
            campaigns.extend(payload.get('data', []))
            after = (payload.get('paging') or {}).get('cursors', {}).get('after', '')
            if not after or not payload.get('data'):
                break
            params['after'] = after
        return campaigns

    def set_campaign_status(self, campaign_id: str, active: bool) -> dict:
        """Pause or resume a campaign."""
        return self._request(
            'POST', campaign_id,
            data={'status': 'ACTIVE' if active else 'PAUSED'},
        )


def extract_conversions(insights_row: dict):
    """Sum the conversion-like actions from an insights row; None when absent."""
    actions = insights_row.get('actions')
    if not isinstance(actions, list):
        return None
    total = 0.0
    found = False
    for action in actions:
        if action.get('action_type') in CONVERSION_ACTION_TYPES:
            try:
                total += float(action.get('value', 0))
                found = True
            except (TypeError, ValueError):
                continue
    return total if found else None
