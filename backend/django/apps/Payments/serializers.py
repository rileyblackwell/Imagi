from rest_framework import serializers
from .models import CreditPackage, Payment, AIModel, AIModelUsage

class CreditPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditPackage
        fields = ['id', 'name', 'amount', 'credits', 'features', 'is_popular']

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
    amount = serializers.DecimalField(required=False, max_digits=10, decimal_places=2, min_value=5, max_value=1000)

    def validate(self, data):
        if not data.get('packageId') and not data.get('amount'):
            raise serializers.ValidationError("Either packageId or amount is required")
        return data

class VerifyPaymentSerializer(serializers.Serializer):
    payment_intent_id = serializers.CharField(required=True)

class CheckUsageAvailabilitySerializer(serializers.Serializer):
    model_id = serializers.IntegerField(required=True) 