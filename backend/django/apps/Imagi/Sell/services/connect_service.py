"""
Stripe Connect for the Sell console.

The founder links their own Stripe account to Imagi's platform account
instead of copying API keys around. Imagi creates a connected account that
the founder owns outright (full Stripe Dashboard; Stripe collects its fees and
covers its losses), then sends them through Stripe's hosted sign-up, where
they either create their Stripe account or log in to the one they have. After
that, Imagi makes every call with its platform key plus the account's id, so
payments are direct charges on the founder's account: they're the merchant,
and the money lands in their Stripe balance, not Imagi's.

Connect has to be switched on for Imagi's own Stripe account (Dashboard →
Connect) before accounts can be created; until it is, Stripe refuses with a
message this module passes on.
"""

import logging

from django.conf import settings as django_settings
from django.utils import timezone

from imagi.redirect_urls import UnsafeRedirectError, resolve_redirect_url

from ..models import SellSettings
from .sell_service import SellServiceError, platform_secret_key
from .stripe_client import StripeClient, StripeClientError

logger = logging.getLogger(__name__)


def _console_url(project, return_path: str, status: str) -> str:
    """Where Stripe sends the founder back: their Sell console."""
    default = f"{django_settings.FRONTEND_URL.rstrip('/')}/imagi/projects"
    try:
        # Only paths inside Imagi: this link is handed to Stripe.
        if return_path and not return_path.startswith('/'):
            raise UnsafeRedirectError('return_path must be a path')
        url = resolve_redirect_url(return_path, default)
    except UnsafeRedirectError:
        url = default
    separator = '&' if '?' in url else '?'
    return f'{url}{separator}stripe={status}'


class ConnectService:
    """Linking one project to its owner's Stripe account."""

    def __init__(self, project):
        self.project = project
        self.config, _ = SellSettings.objects.get_or_create(project=project)

    def _platform(self) -> StripeClient:
        key = platform_secret_key()
        if not key:
            raise SellServiceError(
                'Stripe Connect is not available on this server yet '
                '(Imagi\'s Stripe key is missing). Use your own API keys instead.'
            )
        return StripeClient(key)

    def start_onboarding(self, return_path: str = '') -> str:
        """
        Create the connected account on first use, then a fresh Stripe-hosted
        sign-up link for it. Returns the URL to send the founder to.
        """
        client = self._platform()
        try:
            if not self.config.connect_account_id:
                account = client.create_connected_account(
                    email=(self.project.user.email or ''),
                    metadata={
                        'imagi_project_id': str(self.project.id),
                        'imagi_user_id': str(self.project.user_id),
                    },
                )
                self.config.connect_account_id = account.get('id', '')
                self.config.save(update_fields=['connect_account_id', 'updated_at'])
            link = client.create_onboarding_link(
                self.config.connect_account_id,
                refresh_url=_console_url(self.project, return_path, 'refresh'),
                return_url=_console_url(self.project, return_path, 'return'),
            )
        except StripeClientError as exc:
            message = str(exc)
            if 'Connect' in message:
                message = (
                    'Stripe Connect isn\'t switched on for Imagi\'s Stripe account yet. '
                    f'Stripe said: {exc}'
                )
            raise SellServiceError(message) from exc
        return link.get('url', '')

    def refresh(self) -> dict:
        """Pull the connected account's state from Stripe and cache it."""
        if not self.config.connect_account_id:
            raise SellServiceError('No Stripe account is connected yet.')
        try:
            account = StripeClient(
                platform_secret_key(), self.config.connect_account_id
            ).fetch_account()
        except StripeClientError as exc:
            raise SellServiceError(f'Stripe could not load your account: {exc}') from exc
        self.apply_account(account)
        return account

    def apply_account(self, account: dict) -> None:
        """Cache an account object's flags (from a refresh or account.updated)."""
        dashboard = (account.get('settings') or {}).get('dashboard') or {}
        business = account.get('business_profile') or {}
        self.config.connect_charges_enabled = bool(account.get('charges_enabled'))
        self.config.connect_payouts_enabled = bool(account.get('payouts_enabled'))
        self.config.connect_details_submitted = bool(account.get('details_submitted'))
        self.config.account_name = (
            dashboard.get('display_name') or business.get('name') or self.config.account_name
        )
        self.config.account_email = account.get('email') or self.config.account_email
        self.config.last_verified_at = timezone.now()
        self.config.save(update_fields=[
            'connect_charges_enabled', 'connect_payouts_enabled',
            'connect_details_submitted', 'account_name', 'account_email',
            'last_verified_at', 'updated_at',
        ])

    def disconnect(self) -> None:
        """
        Forget the connected account. The founder's Stripe account and its
        money are untouched; they keep it and can reconnect it later.
        """
        self.config.connect_account_id = ''
        self.config.connect_charges_enabled = False
        self.config.connect_payouts_enabled = False
        self.config.connect_details_submitted = False
        self.config.account_name = ''
        self.config.account_email = ''
        self.config.save(update_fields=[
            'connect_account_id', 'connect_charges_enabled', 'connect_payouts_enabled',
            'connect_details_submitted', 'account_name', 'account_email', 'updated_at',
        ])
