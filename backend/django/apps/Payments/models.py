"""
Models for the Payments app.

Access is sold as subscription plans with a metered dollar allowance
(services/plans.py + services/usage_service.py). Payment, CreditPackage and
Transaction are retained as the historical record of money that changed hands
under the earlier prepaid-credit model; nothing writes new credit balances and
no balance is spendable.
"""

from django.db import models
from django.conf import settings
from decimal import Decimal


class CreditPackage(models.Model):
    """Historical prepaid credit package. Retained for existing Payment rows."""
    id = models.CharField(max_length=50, primary_key=True)  # e.g., 'starter', 'pro', 'enterprise'
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    credits = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    is_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments_credit_package'

    def __str__(self):
        return f"{self.name} (${self.amount} - ${self.credits} credits)"

class Payment(models.Model):
    """Historical record of a completed one-time credit purchase."""

    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    package = models.ForeignKey(CreditPackage, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    credits = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_payment_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments_payment'

    def __str__(self):
        return f"{self.user.email} - ${self.amount:.2f} (${self.credits:.2f} credits)"

    @classmethod
    def calculate_credits(cls, amount):
        """Calculate credits from dollar amount (1:1 ratio)"""
        return Decimal(str(amount))

class PaymentMethod(models.Model):
    """
    Stores user payment methods from Stripe.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payment_methods'
    )
    payment_method_id = models.CharField(max_length=100, unique=True)
    card_brand = models.CharField(max_length=20)  # visa, mastercard, etc.
    last4 = models.CharField(max_length=4)  # Last 4 digits of card
    exp_month = models.PositiveSmallIntegerField()
    exp_year = models.PositiveSmallIntegerField()
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Payment Method'
        verbose_name_plural = 'Payment Methods'
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.user.username}'s {self.card_brand} •••• {self.last4}"
    
    def save(self, *args, **kwargs):
        # If this is set as default, remove default status from other methods
        if self.is_default:
            PaymentMethod.objects.filter(
                user=self.user, 
                is_default=True
            ).update(is_default=False)
        
        super().save(*args, **kwargs)

class StripeCustomer(models.Model):
    """
    Links a user to their Stripe customer.

    Formerly CreditBalance, which also held a spendable dollar balance. Access
    is now metered against a plan allowance rather than drawn from a balance,
    so all this row does is remember the Stripe customer — which subscription
    checkout, the billing portal, and the subscription webhook all resolve
    through.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='stripe_customer'
    )
    stripe_customer_id = models.CharField(max_length=255, blank=True, default='')
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} -> {self.stripe_customer_id or '(none)'}"

    class Meta:
        verbose_name = 'Stripe Customer'
        verbose_name_plural = 'Stripe Customers'

class Subscription(models.Model):
    """
    A user's subscription plan, kept in sync with Stripe by the webhook.

    Plan definitions (names, dollar allowances) live in services/plans.py;
    this row stores only which plan the user is on. Users without a row are on
    the default 'free' plan.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    # Literal rather than services.plans.DEFAULT_PLAN_ID: importing the plan
    # registry here would pull the whole services package (and Stripe) in at
    # model-import time. get_plan() maps any unknown value back to 'free'.
    plan = models.CharField(max_length=50, default='free')
    stripe_subscription_id = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments_subscription'
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'

    def __str__(self):
        return f"{self.user.username} on {self.plan}"


class UsageEvent(models.Model):
    """
    Append-only record of one agent run's usage and metered cost.

    Written by the Build agent after each run whose usage was captured (runs
    with unknown usage are never recorded — absent means unknown, not free).
    Rolling-window plan allowances are computed by summing cost_usd over these
    rows, so no row locking is needed for concurrent runs.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='usage_events'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    model_name = models.CharField(max_length=50)
    input_tokens = models.BigIntegerField(default=0)
    output_tokens = models.BigIntegerField(default=0)
    total_tokens = models.BigIntegerField(default=0)
    # What this run drew from the plan allowance. 6 decimal places because a
    # short run on the cheapest model costs well under a cent, and rounding
    # those to zero would make small runs free.
    cost_usd = models.DecimalField(
        max_digits=12, decimal_places=6, default=Decimal('0')
    )
    # Plain int (not FK) mirroring Build's AgentConversation.project_id style;
    # usage rows must survive conversation deletion for honest metering.
    conversation_id = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'payments_usage_event'
        verbose_name = 'Usage Event'
        verbose_name_plural = 'Usage Events'
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return (
            f"{self.user.username} used ${self.cost_usd} "
            f"({self.total_tokens} tokens, {self.model_name})"
        )


class Transaction(models.Model):
    """
    Records all credit transactions (purchases and usage).
    """
    TRANSACTION_TYPES = [
        ('purchase', 'Purchase'),
        ('usage', 'Usage'),
        ('refund', 'Refund'),
        ('bonus', 'Bonus Credits'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='credit_transactions'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Positive for purchases/bonuses, negative for usage'
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    stripe_payment_intent_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True
    )
    stripe_checkout_session_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount} credits"

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Set description if not provided
        if not self.description:
            if self.transaction_type == 'purchase':
                self.description = f"Credit purchase of {abs(self.amount)} credits"
            elif self.transaction_type == 'usage':
                self.description = f"Usage of {abs(self.amount)} credits"
            elif self.transaction_type == 'refund':
                self.description = f"Refund of {abs(self.amount)} credits"
            elif self.transaction_type == 'bonus':
                self.description = f"Bonus credit award of {abs(self.amount)} credits"
        
        super().save(*args, **kwargs)
