"""
Minimal Google Ads REST API client for the Marketing app.

Talks to the Google Ads REST endpoints directly with `requests` instead of
the google-ads SDK — the ads dashboard only needs to verify the account,
list campaigns with lifetime metrics (one GAQL query), and pause/resume.

Auth is the standard Google Ads API stack the user creates once:
a developer token (API Center), an OAuth client (client_id/client_secret),
and a refresh token authorized for the Ads account. `login_customer_id` is
only needed when access goes through a manager (MCC) account.

API reference: https://developers.google.com/google-ads/api/rest/overview
"""

import logging

import requests

logger = logging.getLogger(__name__)

GOOGLE_ADS_API_VERSION = 'v21'
API_BASE = f'https://googleads.googleapis.com/{GOOGLE_ADS_API_VERSION}'
OAUTH_TOKEN_URL = 'https://oauth2.googleapis.com/token'
REQUEST_TIMEOUT = 20  # seconds

CAMPAIGN_QUERY = """
    SELECT
        campaign.id,
        campaign.name,
        campaign.status,
        campaign.advertising_channel_type,
        campaign_budget.amount_micros,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions
    FROM campaign
    WHERE campaign.status != 'REMOVED'
    ORDER BY metrics.cost_micros DESC
    LIMIT 500
"""

CUSTOMER_QUERY = """
    SELECT customer.descriptive_name, customer.currency_code
    FROM customer
    LIMIT 1
"""


class GoogleAdsError(Exception):
    """Raised when Google Ads can't be reached or returns an error response."""

    def __init__(self, message, status=None, code=None):
        super().__init__(message)
        self.status = status
        self.code = code


class GoogleAdsClient:
    def __init__(self, developer_token: str, client_id: str, client_secret: str,
                 refresh_token: str, customer_id: str, login_customer_id: str = ''):
        if not all([developer_token, client_id, client_secret, refresh_token, customer_id]):
            raise GoogleAdsError(
                'Google Ads requires a developer token, OAuth client ID and secret, '
                'a refresh token, and the customer ID.'
            )
        self.developer_token = developer_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        # Customer IDs are often written 123-456-7890; the API wants digits.
        self.customer_id = str(customer_id).replace('-', '').strip()
        self.login_customer_id = str(login_customer_id or '').replace('-', '').strip()
        self._access_token = ''

    # -- Auth -------------------------------------------------------------------

    def _fetch_access_token(self) -> str:
        """Exchange the refresh token for a short-lived access token."""
        try:
            response = requests.post(
                OAUTH_TOKEN_URL,
                data={
                    'grant_type': 'refresh_token',
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'refresh_token': self.refresh_token,
                },
                timeout=REQUEST_TIMEOUT,
            )
        except requests.RequestException as exc:
            logger.warning(f'Google OAuth token request failed: {exc}')
            raise GoogleAdsError(f'Could not reach Google OAuth: {exc}') from exc

        try:
            payload = response.json()
        except ValueError:
            payload = {}
        if response.status_code >= 400 or 'access_token' not in payload:
            message = payload.get('error_description') or payload.get('error') \
                or f'Google OAuth returned HTTP {response.status_code}'
            raise GoogleAdsError(f'OAuth token refresh failed: {message}',
                                 status=response.status_code)
        return payload['access_token']

    def _headers(self) -> dict:
        if not self._access_token:
            self._access_token = self._fetch_access_token()
        headers = {
            'Authorization': f'Bearer {self._access_token}',
            'developer-token': self.developer_token,
        }
        if self.login_customer_id:
            headers['login-customer-id'] = self.login_customer_id
        return headers

    def _request(self, method: str, path: str, json_body=None) -> dict:
        url = f'{API_BASE}/{path.lstrip("/")}'
        try:
            response = requests.request(
                method, url,
                json=json_body,
                headers=self._headers(),
                timeout=REQUEST_TIMEOUT,
            )
        except requests.RequestException as exc:
            logger.warning(f'Google Ads request failed: {exc}')
            raise GoogleAdsError(f'Could not reach Google Ads: {exc}') from exc

        try:
            payload = response.json()
        except ValueError:
            payload = {}

        if response.status_code >= 400:
            raise GoogleAdsError(
                self._error_message(payload, response.status_code),
                status=response.status_code,
            )
        return payload

    @staticmethod
    def _error_message(payload, http_status) -> str:
        # Errors arrive as {"error": {...}} or, for searchStream, [{"error": {...}}].
        if isinstance(payload, list) and payload:
            payload = payload[0]
        error = payload.get('error') if isinstance(payload, dict) else None
        if isinstance(error, dict):
            details = error.get('details') or []
            for detail in details:
                for item in detail.get('errors', []):
                    if item.get('message'):
                        return item['message']
            if error.get('message'):
                return error['message']
        return f'Google Ads returned HTTP {http_status}'

    def _search(self, query: str) -> list:
        """Run a GAQL query via search, returning the result rows."""
        payload = self._request(
            'POST',
            f'customers/{self.customer_id}/googleAds:search',
            json_body={'query': query},
        )
        return payload.get('results', [])

    # -- Account ------------------------------------------------------------------

    def fetch_customer(self) -> dict:
        """Fetch the customer's name/currency; used to verify credentials."""
        rows = self._search(CUSTOMER_QUERY)
        customer = rows[0].get('customer', {}) if rows else {}
        return {
            'name': customer.get('descriptiveName', ''),
            'currency': customer.get('currencyCode', ''),
        }

    # -- Campaigns ------------------------------------------------------------------

    def list_campaigns(self) -> list:
        """Campaigns with lifetime metrics, as raw GAQL result rows."""
        return self._search(CAMPAIGN_QUERY)

    def set_campaign_status(self, campaign_id: str, active: bool) -> dict:
        """Pause or resume a campaign."""
        resource_name = f'customers/{self.customer_id}/campaigns/{campaign_id}'
        return self._request(
            'POST',
            f'customers/{self.customer_id}/campaigns:mutate',
            json_body={
                'operations': [{
                    'update': {
                        'resourceName': resource_name,
                        'status': 'ENABLED' if active else 'PAUSED',
                    },
                    'updateMask': 'status',
                }],
            },
        )
