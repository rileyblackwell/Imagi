"""
Models for the Operate app — the central hub for running a business.

Everything is scoped to a ProjectManager Project: each user project
(business) gets its own financial ledger (income and expense transactions),
invoices, and operational tasks. The Operate dashboard aggregates these
together with activity from the other workspace modules (e.g. Marketing)
into a single view of how the business is doing.
"""

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Transaction(models.Model):
    """One row in the project's financial ledger: money in or money out."""

    KIND_INCOME = 'income'
    KIND_EXPENSE = 'expense'
    KIND_CHOICES = [
        (KIND_INCOME, 'Income'),
        (KIND_EXPENSE, 'Expense'),
    ]

    # One flat category list shared by both kinds keeps the ledger simple;
    # the API validates that the category matches the transaction kind.
    INCOME_CATEGORIES = ['sales', 'services', 'other_income']
    EXPENSE_CATEGORIES = [
        'supplies', 'software', 'marketing', 'payroll', 'rent',
        'utilities', 'fees', 'taxes', 'other_expense',
    ]
    CATEGORY_CHOICES = [
        ('sales', 'Sales'),
        ('services', 'Services'),
        ('other_income', 'Other income'),
        ('supplies', 'Supplies'),
        ('software', 'Software & tools'),
        ('marketing', 'Marketing'),
        ('payroll', 'Payroll'),
        ('rent', 'Rent'),
        ('utilities', 'Utilities'),
        ('fees', 'Fees'),
        ('taxes', 'Taxes'),
        ('other_expense', 'Other expense'),
    ]

    project = models.ForeignKey(
        'ProjectManager.Project',
        on_delete=models.CASCADE,
        related_name='operate_transactions',
    )
    kind = models.CharField(max_length=10, choices=KIND_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Always positive; `kind` says whether it is money in or out',
    )
    occurred_on = models.DateField(help_text='The date the money moved')
    notes = models.TextField(blank=True, default='')
    invoice = models.ForeignKey(
        'Invoice',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions',
        help_text='Set when this income was recorded by marking an invoice paid',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-occurred_on', '-created_at']
        indexes = [
            models.Index(fields=['project', 'kind']),
            models.Index(fields=['project', 'occurred_on']),
        ]

    def __str__(self):
        sign = '+' if self.kind == self.KIND_INCOME else '-'
        return f"{sign}${self.amount} {self.description} ({self.project.name})"

    @classmethod
    def categories_for_kind(cls, kind: str) -> list:
        return cls.INCOME_CATEGORIES if kind == cls.KIND_INCOME else cls.EXPENSE_CATEGORIES


class Invoice(models.Model):
    """An invoice sent to a customer, with line items stored as JSON."""

    STATUS_DRAFT = 'draft'
    STATUS_SENT = 'sent'
    STATUS_PAID = 'paid'
    STATUS_VOID = 'void'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_SENT, 'Sent'),
        (STATUS_PAID, 'Paid'),
        (STATUS_VOID, 'Void'),
    ]

    # Which status changes are allowed, from -> {to, ...}. "Overdue" is not a
    # stored status — it's derived from due_date on unpaid sent invoices.
    STATUS_TRANSITIONS = {
        STATUS_DRAFT: {STATUS_SENT, STATUS_VOID},
        STATUS_SENT: {STATUS_PAID, STATUS_VOID},
        STATUS_PAID: set(),
        STATUS_VOID: {STATUS_DRAFT},
    }

    project = models.ForeignKey(
        'ProjectManager.Project',
        on_delete=models.CASCADE,
        related_name='operate_invoices',
    )
    number = models.CharField(
        max_length=20,
        help_text='Sequential per project, e.g. INV-0001; assigned on create',
    )
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField(blank=True, default='')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    issue_date = models.DateField(default=timezone.localdate)
    due_date = models.DateField(null=True, blank=True)
    line_items = models.JSONField(
        default=list,
        help_text='List of {"description", "quantity", "unit_price"} objects',
    )
    # Denormalized sum of the line items, kept in sync on save, so lists and
    # dashboard aggregates don't have to unpack JSON.
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    notes = models.TextField(blank=True, default='')
    sent_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'number'],
                name='unique_operate_invoice_number_per_project',
            )
        ]
        indexes = [
            models.Index(fields=['project', 'status']),
        ]

    def __str__(self):
        return f"{self.number} — {self.customer_name} [{self.get_status_display()}]"

    @staticmethod
    def compute_total(line_items) -> Decimal:
        total = Decimal('0.00')
        for item in line_items or []:
            quantity = Decimal(str(item.get('quantity', 0)))
            unit_price = Decimal(str(item.get('unit_price', 0)))
            total += quantity * unit_price
        return total.quantize(Decimal('0.01'))

    @classmethod
    def next_number(cls, project) -> str:
        count = cls.objects.filter(project=project).count()
        return f"INV-{count + 1:04d}"

    @property
    def is_editable(self) -> bool:
        return self.status == self.STATUS_DRAFT

    @property
    def is_overdue(self) -> bool:
        return bool(
            self.status == self.STATUS_SENT
            and self.due_date
            and self.due_date < timezone.localdate()
        )

    def can_transition_to(self, new_status: str) -> bool:
        return new_status in self.STATUS_TRANSITIONS.get(self.status, set())

    def save(self, *args, **kwargs):
        self.total = self.compute_total(self.line_items)
        super().save(*args, **kwargs)


class OperationsTask(models.Model):
    """A to-do for running the business (fulfillment, admin, follow-ups...)."""

    STATUS_TODO = 'todo'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_DONE = 'done'
    STATUS_CHOICES = [
        (STATUS_TODO, 'To do'),
        (STATUS_IN_PROGRESS, 'In progress'),
        (STATUS_DONE, 'Done'),
    ]

    PRIORITY_LOW = 'low'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_HIGH = 'high'
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_MEDIUM, 'Medium'),
        (PRIORITY_HIGH, 'High'),
    ]

    project = models.ForeignKey(
        'ProjectManager.Project',
        on_delete=models.CASCADE,
        related_name='operate_tasks',
    )
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_TODO)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    due_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, default='')
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'status']),
        ]

    def __str__(self):
        return f"{self.title} [{self.get_status_display()}]"

    @property
    def is_overdue(self) -> bool:
        return bool(
            self.status != self.STATUS_DONE
            and self.due_date
            and self.due_date < timezone.localdate()
        )
