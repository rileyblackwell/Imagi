"""
Serializers for the Operate app API.
"""

from decimal import Decimal, InvalidOperation

from rest_framework import serializers

from ..models import Invoice, OperationsTask, Transaction

LINE_ITEMS_MAX = 50


class TransactionSerializer(serializers.ModelSerializer):
    invoice_id = serializers.IntegerField(read_only=True)
    invoice_number = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            'id', 'kind', 'category', 'description', 'amount', 'occurred_on',
            'notes', 'invoice_id', 'invoice_number', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_invoice_number(self, obj) -> str:
        return obj.invoice.number if obj.invoice else ''

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Amount must be greater than zero.')
        return value

    def validate(self, attrs):
        kind = attrs.get('kind', getattr(self.instance, 'kind', None))
        category = attrs.get('category', getattr(self.instance, 'category', None))
        if kind and category and category not in Transaction.categories_for_kind(kind):
            raise serializers.ValidationError(
                {'category': f'"{category}" is not a valid {kind} category.'}
            )
        return attrs

    def create(self, validated_data):
        validated_data['project'] = self.context['project']
        return super().create(validated_data)


class LineItemsField(serializers.ListField):
    """Line items as a list of {description, quantity, unit_price} objects."""

    child = serializers.DictField()

    def to_internal_value(self, data):
        items = super().to_internal_value(data)
        if len(items) > LINE_ITEMS_MAX:
            raise serializers.ValidationError(
                f'Invoices are limited to {LINE_ITEMS_MAX} line items.'
            )
        cleaned = []
        for index, item in enumerate(items):
            description = str(item.get('description', '') or '').strip()
            if not description:
                raise serializers.ValidationError(
                    f'Line item {index + 1} needs a description.'
                )
            try:
                quantity = Decimal(str(item.get('quantity', 1)))
                unit_price = Decimal(str(item.get('unit_price', 0)))
            except (InvalidOperation, ValueError):
                raise serializers.ValidationError(
                    f'Line item {index + 1} has an invalid quantity or price.'
                )
            if quantity <= 0:
                raise serializers.ValidationError(
                    f'Line item {index + 1} quantity must be greater than zero.'
                )
            if unit_price < 0:
                raise serializers.ValidationError(
                    f'Line item {index + 1} price cannot be negative.'
                )
            cleaned.append({
                'description': description[:255],
                # Stored as strings so JSON round-trips without float drift.
                'quantity': str(quantity.quantize(Decimal('0.01')).normalize()),
                'unit_price': str(unit_price.quantize(Decimal('0.01'))),
            })
        return cleaned


class InvoiceSerializer(serializers.ModelSerializer):
    line_items = LineItemsField(required=False)
    total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'number', 'customer_name', 'customer_email', 'status',
            'issue_date', 'due_date', 'line_items', 'total', 'notes',
            'is_overdue', 'sent_at', 'paid_at', 'created_at', 'updated_at',
        ]
        read_only_fields = ['number', 'status', 'sent_at', 'paid_at',
                            'created_at', 'updated_at']

    def validate(self, attrs):
        issue_date = attrs.get('issue_date', getattr(self.instance, 'issue_date', None))
        due_date = attrs.get('due_date', getattr(self.instance, 'due_date', None))
        if issue_date and due_date and due_date < issue_date:
            raise serializers.ValidationError(
                {'due_date': 'Due date cannot be before the issue date.'}
            )
        return attrs

    def create(self, validated_data):
        project = self.context['project']
        validated_data['project'] = project
        validated_data['number'] = Invoice.next_number(project)
        return super().create(validated_data)


class OperationsTaskSerializer(serializers.ModelSerializer):
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = OperationsTask
        fields = [
            'id', 'title', 'status', 'priority', 'due_date', 'notes',
            'is_overdue', 'completed_at', 'created_at', 'updated_at',
        ]
        read_only_fields = ['completed_at', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['project'] = self.context['project']
        return super().create(validated_data)
