# expenses/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Expense, Receipt, Project


# ---------- Formulario de carga ----------
class ExpenseForm(forms.ModelForm):
    """Formulario de carga de gastos (incluye Project/Obra)."""
    class Meta:
        model = Expense
        fields = [
            'date', 'category', 'vendor', 'description', 'amount',
            'payment_method', 'project', 'project_code', 'notes'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Combustible, Materiales'}),
            'vendor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Proveedor'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Detalle'}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'project': forms.Select(attrs={'class': 'form-select'}),      # selector de Obra
            'project_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Obra/PO (texto)'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    # Validación simple
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is None or amount <= 0:
            raise forms.ValidationError("El monto debe ser mayor que 0.")
        return amount


# ---------- Subida de múltiples recibos ----------
class MultipleFileInput(forms.ClearableFileInput):
    """Widget que soporta múltiples archivos."""
    allow_multiple_selected = True


class ReceiptForm(forms.ModelForm):
    image = forms.ImageField(
        widget=MultipleFileInput(attrs={'multiple': True, 'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Receipt
        fields = ['image']


# ---------- Filtros de la lista/export ----------
class ExpenseFilterForm(forms.Form):
    start = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    # Usamos queryset="none" y lo seteamos en __init__ para evitar evaluarlo en import-time
    project = forms.ModelChoiceField(
        queryset=Project.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    # Visible solo para managers (se controla en __init__)
    user = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Poblar querysets ordenados (lo hacemos acá para que siempre refleje la BD actual)
        self.fields['project'].queryset = Project.objects.all().order_by('code', 'name')
        self.fields['project'].empty_label = "Todas las obras"

        # Si es manager mostramos el selector de usuario; si no, lo removemos
        is_manager = bool(
            current_user
            and (current_user.is_superuser or current_user.groups.filter(name__in=['Manager', 'Managers']).exists())
        )
        if is_manager:
            self.fields['user'].queryset = User.objects.all().order_by('username')
            self.fields['user'].empty_label = "Todos los usuarios"
        else:
            # Ocultar el campo a operadores
            self.fields.pop('user', None)

    def clean(self):
        """Validación cruzada: start <= end."""
        cleaned = super().clean()
        start = cleaned.get('start')
        end = cleaned.get('end')
        if start and end and start > end:
            self.add_error('end', 'La fecha "Hasta" debe ser posterior o igual a "Desde".')
        return cleaned
