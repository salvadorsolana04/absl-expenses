from django.db import models
from django.utils.text import slugify

class Expense(models.Model):
    PAYMENT_CHOICES = [
        ('cash', 'Efectivo'),
        ('debit', 'Débito'),
        ('credit', 'Crédito'),
        ('transfer', 'Transferencia'),
        ('check', 'Cheque'),
        ('other', 'Otro'),
    ]

    date = models.DateField('Fecha')
    category = models.CharField('Categoría', max_length=100)
    vendor = models.CharField('Proveedor', max_length=200)
    description = models.CharField('Descripción', max_length=300, blank=True)
    amount = models.DecimalField('Monto', max_digits=12, decimal_places=2)
    payment_method = models.CharField('Medio de pago', max_length=20, choices=PAYMENT_CHOICES)
    project_code = models.CharField('Código/Obra', max_length=50, blank=True)
    notes = models.TextField('Notas', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id or 'new'} · {self.vendor} · ${self.amount}"

class Receipt(models.Model):
    expense = models.ForeignKey(Expense, related_name='receipts', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='receipts/originals/')
    original_name = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        if self.image and not self.original_name:
            self.original_name = self.image.name
        super().save(*args, **kwargs)

    def export_filename(self):
        base = f"EXP-{self.expense_id}-{slugify(self.expense.vendor or 'proveedor')}"
        ext = (self.image.name.split('.')[-1] or 'jpg').lower()
        return f"{base}.{ext}"
