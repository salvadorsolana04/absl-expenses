# expenses/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Project(models.Model):
    """Obra/Job al que se imputa el gasto."""
    name = models.CharField('Nombre de obra', max_length=120, unique=True)
    code = models.CharField('Código', max_length=60, blank=True, db_index=True)
    active = models.BooleanField('Activa', default=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.code or self.name


class Expense(models.Model):
    """Gasto cargado por un operador (con ownership y obra opcional)."""
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

    # NUEVO: relación a Obra/Proyecto (opcional) y dueño del registro
    project = models.ForeignKey(Project, verbose_name='Obra/Proyecto',
                                null=True, blank=True, on_delete=models.SET_NULL)
    created_by = models.ForeignKey(User, verbose_name='Cargado por',
                                   on_delete=models.PROTECT,
                                   null=True, blank=True, related_name='expenses')

    # Campo libre que ya tenías: lo mantenemos por compatibilidad (si después migrás 100% a Project lo retiramos)
    project_code = models.CharField('Código/Obra (texto)', max_length=50, blank=True)

    notes = models.TextField('Notas', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date', '-id')

    def __str__(self):
        return f"{self.id or 'new'} · {self.vendor} · ${self.amount}"


class Receipt(models.Model):
    """Foto/s del ticket asociadas al gasto."""
    expense = models.ForeignKey(Expense, related_name='receipts', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='receipts/originals/')
    original_name = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.image and not self.original_name:
            self.original_name = self.image.name
        super().save(*args, **kwargs)

    def export_filename(self):
        base = f"EXP-{self.expense_id}-{slugify(self.expense.vendor or 'proveedor')}"
        ext = (self.image.name.split('.')[-1] or 'jpg').lower()
        return f"{base}.{ext}"

    def __str__(self):
        return f"Recibo {self.id} de gasto {self.expense_id}"
