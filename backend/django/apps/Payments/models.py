"""
Models for the Payments app.
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal

# Create your models here.

class AIModel(models.Model):
    """Model to track different AI models and their costs"""
    name = models.CharField(max_length=50, unique=True)
    cost_per_use = models.DecimalField(max_digits=6, decimal_places=4)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments_ai_model'

    def __str__(self):
        return f"{self.name} (${self.cost_per_use} per use)"

class AIModelUsage(models.Model):
    """Model to track AI model usage by users"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    model = models.ForeignKey(AIModel, on_delete=models.PROTECT)
    used_at = models.DateTimeField(auto_now_add=True)
    cost = models.DecimalField(max_digits=6, decimal_places=4)
    success = models.BooleanField(default=True)
    context = models.JSONField(default=dict)  # Store additional usage context

    class Meta:
        db_table = 'payments_ai_model_usage'

    def __str__(self):
        return f"{self.user.email} used {self.model.name} at {self.used_at}"

class CreditPackage(models.Model):
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

class CreditBalance(models.Model):
    """
    Tracks a user's credit balance.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='credit_balance'
    )
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    stripe_customer_id = models.CharField(max_length=255, blank=True, default='')
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s balance: {self.balance} credits"

    class Meta:
        verbose_name = 'Credit Balance'
        verbose_name_plural = 'Credit Balances'

class CreditPlan(models.Model):
    """
    Represents a credit purchase plan.
    """
    name = models.CharField(max_length=100)
    credits = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    price_cents = models.PositiveIntegerField()
    stripe_price_id = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.credits} credits for ${self.price_cents/100}"

    class Meta:
        verbose_name = 'Credit Plan'
        verbose_name_plural = 'Credit Plans'
        ordering = ['price_cents']

class Subscription(models.Model):
    """
    A user's subscription plan, kept in sync with Stripe by the webhook.

    Plan definitions (names, token limits) live in services/plans.py; this row
    stores only which plan the user is on. Users without a row are on the
    default 'free' plan.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscription'
    )
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
    Append-only record of one agent run's token usage.

    Written by the Build agent after each run whose usage was captured (runs
    with unknown usage are never recorded — absent means unknown, not free).
    Rolling-window plan limits are computed by summing these rows, so no row
    locking is needed for concurrent runs.
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
        return f"{self.user.username} used {self.total_tokens} tokens ({self.model_name})"


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
