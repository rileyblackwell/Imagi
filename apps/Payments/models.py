from django.db import models

# Create your models here.

class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)
    # Add any other fields you need

    def __str__(self):
        return f"Payment {self.stripe_charge_id} - {'Success' if self.success else 'Failed'}"
