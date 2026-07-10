"""
Serializers for the Sell app API.
"""

import re

from django.db.models import Count, Q, Sum
from rest_framework import serializers

from ..models import Customer, Order, OrderItem, Product, SellSettings
from ..services.sell_service import MIN_PRICE_CENTS, stripe_webhook_url

SECRET_KEY_PATTERN = re.compile(r'^(sk|rk)_[A-Za-z0-9_]+$')
PUBLISHABLE_KEY_PATTERN = re.compile(r'^pk_[A-Za-z0-9_]+$')
WEBHOOK_SECRET_PATTERN = re.compile(r'^whsec_[A-Za-z0-9_]+$')


class SellSettingsSerializer(serializers.ModelSerializer):
    # Secrets are write-only: clients send them once, then only see whether
    # one is stored. They never leave the server after that.
    stripe_secret_key = serializers.CharField(
        write_only=True, required=False, allow_blank=True, trim_whitespace=True
    )
    stripe_webhook_secret = serializers.CharField(
        write_only=True, required=False, allow_blank=True, trim_whitespace=True
    )
    stripe_secret_key_set = serializers.SerializerMethodField()
    stripe_webhook_secret_set = serializers.SerializerMethodField()
    is_configured = serializers.BooleanField(read_only=True)
    stripe_webhook_url = serializers.SerializerMethodField()

    class Meta:
        model = SellSettings
        fields = [
            'stripe_publishable_key',
            'stripe_secret_key',
            'stripe_secret_key_set',
            'stripe_webhook_secret',
            'stripe_webhook_secret_set',
            'currency',
            'account_name',
            'account_email',
            'last_verified_at',
            'is_configured',
            'stripe_webhook_url',
        ]
        read_only_fields = ['account_name', 'account_email', 'last_verified_at']
        extra_kwargs = {
            'stripe_publishable_key': {'required': False, 'allow_blank': True},
            'currency': {'required': False},
        }

    def get_stripe_secret_key_set(self, obj) -> bool:
        return bool(obj.stripe_secret_key_encrypted)

    def get_stripe_webhook_secret_set(self, obj) -> bool:
        return bool(obj.stripe_webhook_secret_encrypted)

    def get_stripe_webhook_url(self, obj) -> str:
        return stripe_webhook_url(obj.project_id)

    def validate_stripe_publishable_key(self, value):
        value = value.strip()
        if value and not PUBLISHABLE_KEY_PATTERN.match(value):
            raise serializers.ValidationError(
                'Publishable key should start with "pk_".'
            )
        return value

    def validate_stripe_secret_key(self, value):
        value = value.strip()
        if value and not SECRET_KEY_PATTERN.match(value):
            raise serializers.ValidationError(
                'Secret key should start with "sk_" (or "rk_" for a restricted key).'
            )
        return value

    def validate_stripe_webhook_secret(self, value):
        value = value.strip()
        if value and not WEBHOOK_SECRET_PATTERN.match(value):
            raise serializers.ValidationError(
                'Webhook signing secret should start with "whsec_".'
            )
        return value

    def update(self, instance, validated_data):
        # An omitted or blank secret means "keep the stored one"; disconnecting
        # the account (clearing the publishable key) also wipes both secrets.
        secret_key = validated_data.pop('stripe_secret_key', '')
        webhook_secret = validated_data.pop('stripe_webhook_secret', '')
        instance = super().update(instance, validated_data)

        update_fields = []
        if secret_key:
            instance.stripe_secret_key = secret_key
            update_fields.append('stripe_secret_key_encrypted')
        if webhook_secret:
            instance.stripe_webhook_secret = webhook_secret
            update_fields.append('stripe_webhook_secret_encrypted')
        if (
            'stripe_publishable_key' in validated_data
            and not instance.stripe_publishable_key
            and not secret_key
            and instance.stripe_secret_key_encrypted
        ):
            instance.stripe_secret_key_encrypted = ''
            instance.stripe_webhook_secret_encrypted = ''
            instance.account_name = ''
            instance.account_email = ''
            update_fields += [
                'stripe_secret_key_encrypted', 'stripe_webhook_secret_encrypted',
                'account_name', 'account_email',
            ]
        if update_fields:
            instance.save(update_fields=update_fields + ['updated_at'])
        return instance


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price_cents', 'image_url',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_price_cents(self, value):
        if value < MIN_PRICE_CENTS:
            raise serializers.ValidationError(
                f'Price must be at least {MIN_PRICE_CENTS} cents — Stripe\'s minimum charge.'
            )
        return value

    def create(self, validated_data):
        validated_data['project'] = self.context['project']
        return super().create(validated_data)


class PublicProductSerializer(serializers.ModelSerializer):
    """The storefront view of a product — safe for unauthenticated callers."""

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price_cents', 'image_url']


class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product_id', 'product_name', 'unit_price_cents', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'status', 'amount_total_cents', 'currency',
            'customer_id', 'customer_email', 'customer_name',
            'stripe_checkout_session_id', 'stripe_payment_intent_id',
            'paid_at', 'fulfilled_at', 'created_at', 'updated_at', 'items',
        ]


class CustomerSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(read_only=True)
    orders_count = serializers.IntegerField(read_only=True, default=0)
    total_spent_cents = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'email', 'display_name', 'phone', 'notes', 'source',
            'orders_count', 'total_spent_cents', 'created_at', 'updated_at',
        ]
        read_only_fields = ['source', 'created_at', 'updated_at']

    def validate_email(self, value):
        value = value.strip().lower()
        project = self.context['project']
        duplicates = Customer.objects.filter(project=project, email=value)
        if self.instance:
            duplicates = duplicates.exclude(id=self.instance.id)
        if duplicates.exists():
            raise serializers.ValidationError('A customer with this email already exists.')
        return value

    def create(self, validated_data):
        validated_data['project'] = self.context['project']
        return super().create(validated_data)


def customers_with_stats(project):
    """Customer queryset annotated with the totals CustomerSerializer reads."""
    return project.sell_customers.annotate(
        orders_count=Count('orders'),
        total_spent_cents=Sum(
            'orders__amount_total_cents',
            filter=Q(orders__status__in=list(Order.PAID_STATUSES)),
            default=0,
        ),
    )
