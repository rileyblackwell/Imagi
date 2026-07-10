"""
Minimal Twilio REST API client for the Marketing app.

Talks to Twilio's HTTP API directly with `requests` instead of pulling in the
full twilio SDK — the marketing module only needs a handful of endpoints:
account verification, sending/fetching/canceling messages, and placing calls.

API reference: https://www.twilio.com/docs/usage/api
"""

import base64
import hashlib
import hmac
import logging

import requests

logger = logging.getLogger(__name__)

API_BASE = 'https://api.twilio.com/2010-04-01'
REQUEST_TIMEOUT = 15  # seconds


class TwilioError(Exception):
    """Raised when Twilio can't be reached or returns an error response."""

    def __init__(self, message, status=None, code=None):
        super().__init__(message)
        self.status = status
        self.code = code


class TwilioClient:
    def __init__(self, account_sid: str, auth_token: str):
        if not account_sid or not auth_token:
            raise TwilioError('Twilio account SID and auth token are required.')
        self.account_sid = account_sid
        self._auth = (account_sid, auth_token)

    def _request(self, method: str, path: str, data=None, params=None) -> dict:
        url = f'{API_BASE}/Accounts/{self.account_sid}{path}'
        try:
            response = requests.request(
                method, url,
                data=data,
                params=params,
                auth=self._auth,
                timeout=REQUEST_TIMEOUT,
            )
        except requests.RequestException as exc:
            logger.warning(f'Twilio request failed: {exc}')
            raise TwilioError(f'Could not reach Twilio: {exc}') from exc

        if response.status_code >= 400:
            message, code = self._parse_error(response)
            raise TwilioError(message, status=response.status_code, code=code)

        if not response.content:
            return {}
        try:
            return response.json()
        except ValueError:
            return {}

    @staticmethod
    def _parse_error(response):
        try:
            payload = response.json()
            return (
                payload.get('message') or f'Twilio returned HTTP {response.status_code}',
                payload.get('code'),
            )
        except ValueError:
            return f'Twilio returned HTTP {response.status_code}', None

    # -- Account ------------------------------------------------------------

    def fetch_account(self) -> dict:
        """Fetch the account resource; used to verify credentials."""
        return self._request('GET', '.json')

    def list_phone_numbers(self) -> list:
        """List the account's incoming phone numbers (first page)."""
        payload = self._request('GET', '/IncomingPhoneNumbers.json', params={'PageSize': 50})
        return payload.get('incoming_phone_numbers', [])

    # -- Programmable Messaging ----------------------------------------------

    def send_message(self, to: str, body: str, from_number: str = '',
                     messaging_service_sid: str = '', status_callback: str = '',
                     send_at: str = '') -> dict:
        """
        Send an SMS. When `send_at` (ISO 8601 UTC) is given, Twilio holds the
        message and delivers it at that time — this requires a Messaging
        Service SID.
        """
        data = {'To': to, 'Body': body}
        if messaging_service_sid:
            data['MessagingServiceSid'] = messaging_service_sid
        elif from_number:
            data['From'] = from_number
        if status_callback:
            data['StatusCallback'] = status_callback
        if send_at:
            data['SendAt'] = send_at
            data['ScheduleType'] = 'fixed'
        return self._request('POST', '/Messages.json', data=data)

    def fetch_message(self, sid: str) -> dict:
        return self._request('GET', f'/Messages/{sid}.json')

    def cancel_message(self, sid: str) -> dict:
        """Cancel a scheduled (not yet sent) message."""
        return self._request('POST', f'/Messages/{sid}.json', data={'Status': 'canceled'})

    # -- Programmable Voice ---------------------------------------------------

    def create_call(self, to: str, from_number: str, twiml: str,
                    status_callback: str = '') -> dict:
        """Place an outbound call that plays the given TwiML (e.g. a <Say>)."""
        data = {'To': to, 'From': from_number, 'Twiml': twiml}
        if status_callback:
            data['StatusCallback'] = status_callback
        return self._request('POST', '/Calls.json', data=data)

    def fetch_call(self, sid: str) -> dict:
        return self._request('GET', f'/Calls/{sid}.json')


def validate_webhook_signature(auth_token: str, url: str, params: dict, signature: str) -> bool:
    """
    Validate an X-Twilio-Signature header: HMAC-SHA1 (base64) of the full
    request URL with the POST params appended in key-sorted order.
    https://www.twilio.com/docs/usage/security#validating-requests
    """
    if not auth_token or not signature:
        return False
    payload = url + ''.join(key + value for key, value in sorted(params.items()))
    digest = hmac.new(auth_token.encode(), payload.encode('utf-8'), hashlib.sha1).digest()
    expected = base64.b64encode(digest).decode()
    return hmac.compare_digest(expected, signature)
