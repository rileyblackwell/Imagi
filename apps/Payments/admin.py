from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'credits', 'stripe_payment_id', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'stripe_payment_id')
    readonly_fields = ('stripe_payment_id', 'created_at')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('user', 'amount', 'credits')
        return self.readonly_fields
