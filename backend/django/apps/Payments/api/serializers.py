"""
Serializers for the Payments app API.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import CreditBalance, Transaction, CreditPlan

User = get_user_model()

class CreditBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditBalance
        fields = ('id', 'user', 'balance', 'last_updated')
        read_only_fields = ('id', 'last_updated')

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('id', 'user', 'amount', 'transaction_type', 'status', 
                 'stripe_payment_intent_id', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

class CreditPlanSerializer(serializers.ModelSerializer):
    price_in_dollars = serializers.SerializerMethodField()
    
    class Meta:
        model = CreditPlan
        fields = ('id', 'name', 'credits', 'price_cents', 'price_in_dollars', 
                 'stripe_price_id', 'is_active')
        read_only_fields = ('id',)
    
    def get_price_in_dollars(self, obj):
        """Convert price from cents to dollars for display."""
        return float(obj.price_cents) / 100

class UserCreditBalanceSerializer(serializers.ModelSerializer):
    credit_balance = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'credit_balance')
        read_only_fields = ('id', 'username', 'email', 'credit_balance')
    
    def get_credit_balance(self, obj):
        """Get the user's current credit balance."""
        try:
            balance = CreditBalance.objects.get(user=obj)
            return float(balance.balance)
        except CreditBalance.DoesNotExist:
            return 0.0 