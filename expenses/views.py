from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView
from django.contrib import messages
from django.http import HttpResponse
from .models import Expense, Receipt
from .forms import ExpenseForm, ReceiptForm
from .utils import build_export

class ExpenseCreateView(View):
    template_name = 'expenses/expense_form.html'

    def get(self, request):
        return render(request, self.template_name, {
            'form': ExpenseForm(),
            'rform': ReceiptForm(),
        })

    def post(self, request):
        form = ExpenseForm(request.POST)
        rform = ReceiptForm(request.POST, request.FILES)
        files = request.FILES.getlist('image')
        if form.is_valid():
            expense = form.save()
            for f in files:
                Receipt.objects.create(expense=expense, image=f)
            messages.success(request, 'Gasto cargado correctamente. Podés cargar otro.')
            # Reset: redirect to blank form
            return redirect(reverse('expense-create'))
        messages.error(request, 'Revisá los campos.')
        return render(request, self.template_name, {'form': form, 'rform': rform})

class ExpenseListView(ListView):
    model = Expense
    template_name = 'expenses/expense_list.html'
    context_object_name = 'expenses'
    paginate_by = 20
    ordering = ['-date','-id']


def export_zip(request):
    qs = Expense.objects.all()
    buf = build_export(qs)
    resp = HttpResponse(buf.getvalue(), content_type='application/zip')
    resp['Content-Disposition'] = 'attachment; filename="absl-expenses-export.zip"'
    return resp
