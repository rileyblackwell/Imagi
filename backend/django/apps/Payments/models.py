from django.db import models
from django.conf import settings
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
