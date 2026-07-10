"""
Models for the Sell app.

Everything here is scoped to a ProjectManager Project: each user project
(business) gets its own Stripe configuration, product catalog, customers,
and order history. Stripe is the payment layer — customers pay through
Stripe Checkout sessions created against the project owner's own Stripe
account (bring-your-own API keys, like Marketing's Twilio credentials).
"""

import base64
import hashlib
import logging

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    def is_configured(self) -> bool:
        """True when there is a secret key to create checkout sessions with."""
        return bool(self.stripe_secret_key_encrypted)


class Product(models.Model):
    """Something a project's business sells — one line in the catalog."""

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
    is_active = models.BooleanField(
        default=True,
        help_text='Only active products can be bought',
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
