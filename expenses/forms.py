from django import forms
from .models import Expense, Receipt

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = [
            'date','category','vendor','description','amount',
            'payment_method','project_code','notes'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Combustible, Materiales'}),
            'vendor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Proveedor'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Detalle'}),
            'amount': forms.NumberInput(attrs={'step': '0.01','class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'project_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Obra/PO'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows':3}),
        }

# 👇 widget que sí acepta múltiples archivos
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class ReceiptForm(forms.ModelForm):
    image = forms.ImageField(
        widget=MultipleFileInput(attrs={'multiple': True, 'class': 'form-control'}),
        required=False
    )
    class Meta:
        model = Receipt
        fields = ['image']
