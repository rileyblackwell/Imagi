"""
Models for the Sell app.

Everything here is scoped to a ProjectManager Project: each user project
(business) gets its own Stripe configuration, product catalog, customers,
and order history. Stripe is the payment layer — customers pay through
Stripe Checkout sessions created against the project owner's own Stripe
account. The owner connects that account through Stripe Connect (Stripe's
hosted sign-up, no keys to copy), or, as an advanced fallback, pastes their
own API keys.
"""

import base64
import hashlib
import logging
import secrets

from django.conf import settings
from django.db import models

logger = logging.getLogger(__name__)


def _fernet():
    """Fernet keyed off SECRET_KEY, used to encrypt Stripe credentials at rest."""
    from cryptography.fernet import Fernet
    digest = hashlib.sha256(
        ('imagi.sell.stripe:' + settings.SECRET_KEY).encode()
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
        logger.warning('Could not decrypt a stored Stripe credential; treating it as unset.')
        return ''


class SellSettings(models.Model):
    """Per-project Stripe configuration for the sell workspace."""

    CURRENCY_CHOICES = [
        ('usd', 'USD — US Dollar'),
        ('eur', 'EUR — Euro'),
        ('gbp', 'GBP — British Pound'),
        ('cad', 'CAD — Canadian Dollar'),
        ('aud', 'AUD — Australian Dollar'),
    ]

    project = models.OneToOneField(
        'ProjectManager.Project',
        on_delete=models.CASCADE,
        related_name='sell_settings',
    )
    stripe_publishable_key = models.CharField(max_length=255, blank=True, default='')
    # Encrypted with a SECRET_KEY-derived Fernet key; use the
    # `stripe_secret_key` property to read/write the plaintext value.
    stripe_secret_key_encrypted = models.TextField(blank=True, default='')
    # Signing secret (whsec_...) for the project's Stripe webhook endpoint;
    # read/write plaintext via the `stripe_webhook_secret` property.
    stripe_webhook_secret_encrypted = models.TextField(blank=True, default='')
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='usd',
        help_text='Currency for all products and checkout sessions',
    )
    account_name = models.CharField(max_length=255, blank=True, default='')
    account_email = models.CharField(max_length=255, blank=True, default='')
    last_verified_at = models.DateTimeField(null=True, blank=True)

    # Stripe Connect: the owner's own Stripe account, linked to Imagi's
    # platform account. Imagi calls Stripe with its platform key on the
    # account's behalf, so no keys of theirs are stored. Charges are direct
    # charges on their account: they are the merchant, and the money is theirs.
    connect_account_id = models.CharField(max_length=255, blank=True, default='', db_index=True)
    connect_charges_enabled = models.BooleanField(default=False)
    connect_payouts_enabled = models.BooleanField(default=False)
    connect_details_submitted = models.BooleanField(default=False)

    # How the business charges, chosen in the console: any of 'one_time',
    # 'subscription' and 'usage'. Decides which pages the payment template
    # adds to the app.
    payment_models = models.JSONField(default=list, blank=True)

    # Where the business's app lives once it is published. Stripe may send
    # customers back there after checkout (see sell_service.redirect origins).
    app_url = models.URLField(max_length=500, blank=True, default='')

    # Server key: lets the business's own backend report usage and check a
    # customer's subscription. Encrypted, like the Stripe secrets; read via
    # the `server_key` property.
    server_key_encrypted = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    PAYMENT_MODELS = ('one_time', 'subscription', 'usage')
    SERVER_KEY_PREFIX = 'imagi_sk_'

    class Meta:
        verbose_name = 'Sell Settings'
        verbose_name_plural = 'Sell Settings'

    def __str__(self):
        return f"Sell settings for {self.project.name}"

    @property
    def stripe_secret_key(self) -> str:
        return decrypt_secret(self.stripe_secret_key_encrypted)

    @stripe_secret_key.setter
    def stripe_secret_key(self, value: str):
        self.stripe_secret_key_encrypted = encrypt_secret(value)

    @property
    def stripe_webhook_secret(self) -> str:
        return decrypt_secret(self.stripe_webhook_secret_encrypted)

    @stripe_webhook_secret.setter
    def stripe_webhook_secret(self, value: str):
        self.stripe_webhook_secret_encrypted = encrypt_secret(value)

    @property
    def server_key(self) -> str:
        return decrypt_secret(self.server_key_encrypted)

    def rotate_server_key(self) -> str:
        """Issue a new server key, replacing any old one. Caller saves."""
        key = self.SERVER_KEY_PREFIX + secrets.token_urlsafe(32)
        self.server_key_encrypted = encrypt_secret(key)
        return key

    def check_server_key(self, candidate: str) -> bool:
        stored = self.server_key
        return bool(stored) and bool(candidate) and secrets.compare_digest(
            stored.encode(), candidate.encode()
        )

    @property
    def uses_connect(self) -> bool:
        """Connected through Stripe Connect (preferred over pasted keys)."""
        return bool(self.connect_account_id)

    @property
    def connection_type(self) -> str:
        if self.uses_connect:
            return 'connect'
        if self.stripe_secret_key_encrypted:
            return 'keys'
        return ''

    @property
    def is_configured(self) -> bool:
        """True when Imagi can create checkout sessions for this project."""
        if self.uses_connect:
            return self.connect_charges_enabled
        return bool(self.stripe_secret_key_encrypted)

    @property
    def is_test_mode(self) -> bool:
        """Whether checkouts run against Stripe's test mode."""
        if self.uses_connect:
            from django.conf import settings as django_settings
            key = getattr(django_settings, 'STRIPE_SECRET_KEY', '') or ''
            return not key.startswith(('sk_live_', 'rk_live_'))
        return not self.stripe_secret_key.startswith(('sk_live_', 'rk_live_'))


class Product(models.Model):
    """Something a project's business sells — one line in the catalog."""

    BILLING_ONE_TIME = 'one_time'
    BILLING_MONTH = 'month'
    BILLING_YEAR = 'year'
    # Pay as you go: a monthly subscription billed on metered usage that the
    # business's backend reports (Stripe Billing meters).
    BILLING_USAGE = 'usage'
    BILLING_CHOICES = [
        (BILLING_ONE_TIME, 'One-time purchase'),
        (BILLING_MONTH, 'Monthly subscription'),
        (BILLING_YEAR, 'Yearly subscription'),
        (BILLING_USAGE, 'Pay as you go'),
    ]

    project = models.ForeignKey(
        'ProjectManager.Project',
        on_delete=models.CASCADE,
        related_name='sell_products',
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    # Stored in the smallest currency unit (cents); the currency itself lives
    # on SellSettings so a project's catalog can't mix currencies (a Stripe
    # Checkout session only accepts one currency across its line items).
    price_cents = models.PositiveIntegerField(
        help_text='Price in the smallest currency unit, e.g. cents',
    )
    image_url = models.URLField(max_length=500, blank=True, default='')
    # One-time purchase, or the cadence Stripe bills at when this product is
    # a subscription (checkout switches to subscription mode).
    billing_interval = models.CharField(
        max_length=10,
        choices=BILLING_CHOICES,
        default=BILLING_ONE_TIME,
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Only active products can be bought',
    )
    # Pay as you go only: what one unit is ("API call", "message") and how
    # many units `price_cents` buys, so "$1 per 1,000 messages" needs no
    # fractions of a cent.
    usage_unit_label = models.CharField(max_length=60, blank=True, default='')
    usage_unit_count = models.PositiveIntegerField(default=1)

    # Stripe objects a pay-as-you-go product needs on the merchant's account:
    # metered prices can't be built inline at checkout. Created on first
    # checkout; `stripe_price_signature` notices a changed price, since
    # Stripe prices are immutable and a new one is made instead.
    stripe_meter_id = models.CharField(max_length=255, blank=True, default='')
    stripe_meter_event_name = models.CharField(max_length=100, blank=True, default='')
    stripe_price_id = models.CharField(max_length=255, blank=True, default='')
    stripe_price_signature = models.CharField(max_length=255, blank=True, default='')
    stripe_account_ref = models.CharField(
        max_length=255, blank=True, default='',
        help_text='The Stripe account the meter and price above live on',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.project.name})"

    @property
    def is_recurring(self) -> bool:
        return self.billing_interval != self.BILLING_ONE_TIME

    @property
    def is_usage(self) -> bool:
        return self.billing_interval == self.BILLING_USAGE

    @property
    def pricing_model(self) -> str:
        """The console's three ways to charge: one_time, subscription, usage."""
        if self.billing_interval == self.BILLING_ONE_TIME:
            return 'one_time'
        if self.is_usage:
            return 'usage'
        return 'subscription'


class Customer(models.Model):
    """A person who bought from (or was added to) a project's business."""

    SOURCE_CHOICES = [
        ('manual', 'Added manually'),
        ('checkout', 'Stripe checkout'),
    ]

    project = models.ForeignKey(
        'ProjectManager.Project',
        on_delete=models.CASCADE,
        related_name='sell_customers',
    )
    name = models.CharField(max_length=255, blank=True, default='')
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, default='')
    notes = models.TextField(blank=True, default='')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='manual')
    # Their Stripe customer on the merchant's account, once they've checked
    # out; usage is reported against it.
    stripe_customer_id = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'email'],
                name='unique_sell_customer_email_per_project',
            )
        ]

    def __str__(self):
        return f"{self.display_name} ({self.project.name})"

    @property
    def display_name(self) -> str:
        return self.name or self.email


class Order(models.Model):
    """
    One checkout attempt and its outcome.

    Created as `pending` alongside the Stripe Checkout session; the webhook
    (or a manual sync from Stripe) moves it to `paid`, the owner marks it
    `fulfilled`, and refunds/expired sessions land in `refunded`/`canceled`.
    """

    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_FULFILLED = 'fulfilled'
    STATUS_CANCELED = 'canceled'
    STATUS_REFUNDED = 'refunded'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending payment'),
        (STATUS_PAID, 'Paid'),
        (STATUS_FULFILLED, 'Fulfilled'),
        (STATUS_CANCELED, 'Canceled'),
        (STATUS_REFUNDED, 'Refunded'),
    ]

    # Statuses that count toward revenue.
    PAID_STATUSES = {STATUS_PAID, STATUS_FULFILLED}

    project = models.ForeignKey(
        'ProjectManager.Project',
        on_delete=models.CASCADE,
        related_name='sell_orders',
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    amount_total_cents = models.PositiveIntegerField(default=0)
    currency = models.CharField(max_length=3, default='usd')
    # Snapshot from Stripe's customer_details after payment.
    customer_email = models.EmailField(blank=True, default='')
    customer_name = models.CharField(max_length=255, blank=True, default='')
    stripe_checkout_session_id = models.CharField(
        max_length=255, blank=True, default='', db_index=True,
    )
    stripe_payment_intent_id = models.CharField(
        max_length=255, blank=True, default='', db_index=True,
    )
    paid_at = models.DateTimeField(null=True, blank=True)
    fulfilled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['project', '-created_at']),
        ]

    def __str__(self):
        return f"Order #{self.id} [{self.get_status_display()}] ({self.project.name})"


class OrderItem(models.Model):
    """One product line on an order, with name/price snapshotted at purchase."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items',
    )
    product_name = models.CharField(max_length=255)
    unit_price_cents = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} × {self.product_name}"


class Subscription(models.Model):
    """A customer's recurring plan (fixed or pay as you go), mirrored from Stripe."""

    # Stripe's subscription statuses that still grant access.
    ACTIVE_STATUSES = {'active', 'trialing', 'past_due'}

    project = models.ForeignKey(
        'ProjectManager.Project',
        on_delete=models.CASCADE,
        related_name='sell_subscriptions',
    )
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='subscriptions',
    )
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='subscriptions',
    )
    product_name = models.CharField(max_length=255, blank=True, default='')
    customer_email = models.EmailField(blank=True, default='')
    stripe_subscription_id = models.CharField(max_length=255)
    stripe_customer_id = models.CharField(max_length=255, blank=True, default='')
    # Stripe's own status: active, trialing, past_due, canceled, unpaid, ...
    status = models.CharField(max_length=30, default='incomplete')
    cancel_at_period_end = models.BooleanField(default=False)
    current_period_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'stripe_subscription_id'],
                name='unique_sell_subscription_per_project',
            )
        ]
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['project', 'customer_email']),
        ]

    def __str__(self):
        return f"{self.product_name or 'Subscription'} for {self.customer_email} [{self.status}]"

    @property
    def is_active(self) -> bool:
        return self.status in self.ACTIVE_STATUSES


class UsageEvent(models.Model):
    """One usage report from the business's backend, forwarded to Stripe."""

    project = models.ForeignKey(
        'ProjectManager.Project',
        on_delete=models.CASCADE,
        related_name='sell_usage_events',
    )
    subscription = models.ForeignKey(
        Subscription, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='usage_events',
    )
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='usage_events',
    )
    customer_email = models.EmailField()
    quantity = models.PositiveIntegerField()
    # Caller-chosen key so a retried report is only counted once (Stripe
    # also dedupes meter events by this identifier).
    idempotency_key = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'idempotency_key'],
                name='unique_sell_usage_event_key_per_project',
            )
        ]
        indexes = [
            models.Index(fields=['project', '-created_at']),
        ]

    def __str__(self):
        return f"{self.quantity} for {self.customer_email}"
