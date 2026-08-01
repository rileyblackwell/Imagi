"""
Serializers for the Payments app API.

Only the read-only history surfaces need serializers: plans and usage are
code-defined dicts (services/plans.py) rather than models, and there is no
longer a balance to serialize.
"""

from rest_framework import serializers
from ..models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    model = serializers.SerializerMethodField()
    request_type = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ('id', 'user', 'amount', 'transaction_type', 'status',
                 'stripe_payment_intent_id', 'created_at', 'updated_at', 'description', 'model', 'request_type')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_model(self, obj):
        # Historical usage rows encoded the model in the description, e.g.
        # "GPT 5.6 Terra - build template: $0.04".
        if obj.transaction_type == 'usage' and obj.description:
            parts = obj.description.split(' - ')
            if len(parts) > 1:
                return parts[0].strip()
        return None

    def get_request_type(self, obj):
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
        if obj.transaction_type == 'usage' and obj.description:
            parts = obj.description.split(' - ')
            if len(parts) > 1:
                return parts[0].strip()
        return None

    def get_request_type(self, obj):
        if obj.transaction_type == 'usage' and obj.description:
            parts = obj.description.split(' - ')
            if len(parts) > 1 and ':' in parts[1]:
                return parts[1].split(':')[0].strip()
        return None
