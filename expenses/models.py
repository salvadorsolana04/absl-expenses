# expenses/models.py
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Project(models.Model):
    """Job/Project to assign expenses to."""
    name = models.CharField('Job name', max_length=120, unique=True)
    code = models.CharField('Code', max_length=60, blank=True, db_index=True)
    active = models.BooleanField('Active', default=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.code or self.name


# NEW: cost types
COST_CHOICES = (
    ("JOB", "Job cost"),
    ("EQ", "Equipment cost"),
)


class Expense(models.Model):
    """Expense uploaded by an operator (with ownership and optional job)."""
    PAYMENT_CHOICES = [
        ('cash', 'Cash'),
        ('debit', 'Debit'),
        ('credit', 'Credit'),
        ('transfer', 'Transfer'),
        ('check', 'Check'),
        ('other', 'Other'),
    ]

    date = models.DateField('Date')
    category = models.CharField('Category', max_length=100)
    vendor = models.CharField('Vendor', max_length=200)
    description = models.CharField('Description', max_length=300, blank=True)

    # amount acts as TOTAL; it will be auto-calculated from quantity * unit_price
    amount = models.DecimalField('Total', max_digits=12, decimal_places=2)

    # Kept for backward compatibility (no longer shown in the form)
    payment_method = models.CharField('Payment method', max_length=20, choices=PAYMENT_CHOICES)

    # NEW fields
    cost_type = models.CharField('Cost', max_length=10, choices=COST_CHOICES, default="JOB", db_index=True)
    account = models.CharField('Account', max_length=50, blank=True, default="")
    subaccount = models.CharField('Subaccount', max_length=50, blank=True, default="")
    quantity = models.DecimalField('Quantity', max_digits=10, decimal_places=2, default=Decimal("1.00"))
    unit_price = models.DecimalField('Price', max_digits=10, decimal_places=2, default=Decimal("0.00"))

    # Relations / ownership
    project = models.ForeignKey(
        Project, verbose_name='Job/Project',
        null=True, blank=True, on_delete=models.SET_NULL
    )
    created_by = models.ForeignKey(
        User, verbose_name='Uploaded by',
        on_delete=models.PROTECT, null=True, blank=True, related_name='expenses'
    )

    # Free text code kept: now shown as "Job/EQ#"
    project_code = models.CharField('Job/EQ#', max_length=50, blank=True)

    notes = models.TextField('Notes', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date', '-id')

    def save(self, *args, **kwargs):
        # Auto-calc total from qty * price
        try:
            self.amount = (self.quantity or 0) * (self.unit_price or 0)
        except Exception:
            pass
        super().save(*args, **kwargs)

    @property
    def total(self):
        return self.amount or ((self.quantity or 0) * (self.unit_price or 0))

    def __str__(self):
        return f"{self.id or 'new'} · {self.vendor} · ${self.amount}"


class Receipt(models.Model):
    """Ticket photo(s) associated to an expense."""
    expense = models.ForeignKey(Expense, related_name='receipts', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='receipts/originals/')
    original_name = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.image and not self.original_name:
            self.original_name = self.image.name
        super().save(*args, **kwargs)

    def export_filename(self):
        base = f"EXP-{self.expense_id}-{slugify(self.expense.vendor or 'vendor')}"
        ext = (self.image.name.split('.')[-1] or 'jpg').lower()
        return f"{base}.{ext}"

    def __str__(self):
        return f"Receipt {self.id} for expense {self.expense_id}"
