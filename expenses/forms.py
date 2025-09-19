# expenses/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Expense, Receipt, Project, COST_CHOICES


# ---------- Expense entry form ----------
class ExpenseForm(forms.ModelForm):
    """Expense entry form (English) with cost type and job code."""
    class Meta:
        model = Expense
        fields = [
            'date', 'category', 'vendor',
            'account', 'subaccount',      # NEW: shown above description
            'description',
            'quantity', 'unit_price',     # NEW
            'cost_type',                  # NEW: Job/Equipment cost
            'project', 'project_code',    # project_code label = Job/EQ#
            'notes',
        ]
        labels = {
            'date': 'Date',
            'category': 'Category',
            'vendor': 'Vendor',
            'account': 'Account',
            'subaccount': 'Subaccount',
            'description': 'Description',
            'quantity': 'Quantity',
            'unit_price': 'Price',
            'cost_type': 'Cost',
            'project': 'Job',
            'project_code': 'Job/EQ#',
            'notes': 'Notes',
        }
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Fuel, Materials'}),
            'vendor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vendor'}),
            'account': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account'}),
            'subaccount': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subaccount'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Short description'}),
            'quantity': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'cost_type': forms.Select(choices=COST_CHOICES, attrs={'class': 'form-select'}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'project_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job/EQ# (text)'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    # amount/total is calculated in model.save()
    def clean_quantity(self):
        q = self.cleaned_data.get('quantity')
        if q is None or q <= 0:
            raise forms.ValidationError("Quantity must be greater than 0.")
        return q

    def clean_unit_price(self):
        p = self.cleaned_data.get('unit_price')
        if p is None or p < 0:
            raise forms.ValidationError("Price must be 0 or greater.")
        return p


# ---------- Multiple receipts upload ----------
class MultipleFileInput(forms.ClearableFileInput):
    """Widget supporting multiple files."""
    allow_multiple_selected = True


class ReceiptForm(forms.ModelForm):
    image = forms.ImageField(
        widget=MultipleFileInput(attrs={'multiple': True, 'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Receipt
        fields = ['image']


# ---------- Filters (kept) ----------
class ExpenseFilterForm(forms.Form):
    start = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    project = forms.ModelChoiceField(
        queryset=Project.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    user = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['project'].queryset = Project.objects.all().order_by('code', 'name')
        self.fields['project'].empty_label = "All jobs"

        is_manager = bool(
            current_user
            and (current_user.is_superuser or current_user.groups.filter(name__in=['Manager', 'Managers']).exists())
        )
        if is_manager:
            self.fields['user'].queryset = User.objects.all().order_by('username')
            self.fields['user'].empty_label = "All users"
        else:
            self.fields.pop('user', None)

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start')
        end = cleaned.get('end')
        if start and end and start > end:
            self.add_error('end', '"To" date must be greater than or equal to "From" date.')
        return cleaned
