"""
Serializers for the Payments app API.
"""

from rest_framework import serializers
from decimal import Decimal
from django.contrib.auth import get_user_model
from ..models import CreditBalance, Transaction, CreditPlan, CreditPackage, Payment, AIModel, AIModelUsage, PaymentMethod

User = get_user_model()

class CreditBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditBalance
        fields = ('id', 'user', 'balance', 'last_updated')
        read_only_fields = ('id', 'last_updated')

class TransactionSerializer(serializers.ModelSerializer):
    model = serializers.SerializerMethodField()
    request_type = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ('id', 'user', 'amount', 'transaction_type', 'status', 
                 'stripe_payment_intent_id', 'created_at', 'updated_at', 'description', 'model', 'request_type')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_model(self, obj):
        # Try to extract model from description, e.g. "Claude Sonnet 3.7 - build template: $0.04"
        if obj.transaction_type == 'usage' and obj.description:
            parts = obj.description.split(' - ')
            if len(parts) > 1:
                return parts[0].strip()
        return None

    def get_request_type(self, obj):
        # Try to extract request type from description, e.g. "Claude Sonnet 3.7 - build template: $0.04"
        if obj.transaction_type == 'usage' and obj.description:
            parts = obj.description.split(' - ')
            if len(parts) > 1 and ':' in parts[1]:
                return parts[1].split(':')[0].strip()
        return None


class PaymentHistorySerializer(serializers.ModelSerializer):
    """Serializer for payment history items displayed in the frontend."""
    model = serializers.SerializerMethodField()
    request_type = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ('id', 'amount', 'status', 'created_at', 'description', 'model', 'request_type')
        read_only_fields = ('id', 'created_at')
    
    def to_representation(self, instance):
        """Format the data to match what the frontend expects."""
        representation = super().to_representation(instance)
        # Make sure all transaction amounts are positive for display
        representation['amount'] = abs(float(instance.amount))
        representation['created_at'] = instance.created_at.isoformat()
        return representation

    def get_model(self, obj):
        # Try to extract model from description, e.g. "Claude Sonnet 3.7 - build template: $0.04"
        if obj.transaction_type == 'usage' and obj.description:
            parts = obj.description.split(' - ')
            if len(parts) > 1:
                return parts[0].strip()
        return None

    def get_request_type(self, obj):
        # Try to extract request type from description, e.g. "Claude Sonnet 3.7 - build template: $0.04"
        if obj.transaction_type == 'usage' and obj.description:
            parts = obj.description.split(' - ')
            if len(parts) > 1 and ':' in parts[1]:
                return parts[1].split(':')[0].strip()
        return None


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

class CreditPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditPackage
        fields = ['id', 'name', 'amount', 'credits', 'features', 'is_popular']

class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer for saved payment methods."""
    
    class Meta:
        model = PaymentMethod
        fields = ['id', 'user', 'payment_method_id', 'card_brand', 'last4', 
                 'exp_month', 'exp_year', 'is_default', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def to_representation(self, instance):
        """Format payment method data as expected by frontend."""
        representation = super().to_representation(instance)
        # Add friendly display name
        representation['display_name'] = f"{instance.card_brand} •••• {instance.last4}"
        return representation

class PaymentSerializer(serializers.ModelSerializer):
    package_name = serializers.CharField(source='package.name', read_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'amount', 'credits', 'status', 'created_at', 'package_name']
        read_only_fields = ['status', 'created_at']

class AIModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIModel
        fields = ['id', 'name', 'cost_per_use', 'description']

class AIModelUsageSerializer(serializers.ModelSerializer):
    model_name = serializers.CharField(source='model.name', read_only=True)
    
    class Meta:
        model = AIModelUsage
        fields = ['id', 'model_name', 'cost', 'used_at', 'success', 'context']
        read_only_fields = ['used_at']

class CreatePaymentIntentSerializer(serializers.Serializer):
    packageId = serializers.CharField(required=False, allow_null=True)
    amount = serializers.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('5.00'),
        max_value=Decimal('1000.00')
    )

    def validate(self, data):
        if not data.get('packageId') and not data.get('amount'):
            raise serializers.ValidationError("Either packageId or amount is required")
        return data

class VerifyPaymentSerializer(serializers.Serializer):
    payment_intent_id = serializers.CharField(required=True)

class CheckUsageAvailabilitySerializer(serializers.Serializer):
    model_id = serializers.IntegerField(required=True) 