from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('stripe_charge_id', 'amount', 'timestamp', 'success')
    search_fields = ('stripe_charge_id',)
    list_filter = ('success', 'timestamp')
