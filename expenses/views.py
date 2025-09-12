# expenses/views.py
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView
from django.contrib import messages
from django.http import HttpResponse

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Expense, Receipt, Project
from .forms import ExpenseForm, ReceiptForm, ExpenseFilterForm
from .utils import build_export


# --- Helper: ¿el usuario es manager? ---
def is_manager(user):
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name__in=["Manager", "Managers"]).exists()
    )


# --- Crear gasto ---
@method_decorator(login_required, name='dispatch')  # ⬅️ NEW: requiere login para GET/POST
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
            expense = form.save(commit=False)
            # Con login obligatorio, siempre seteamos owner
            expense.created_by = request.user
            expense.save()

            for f in files:
                Receipt.objects.create(expense=expense, image=f)

            messages.success(request, 'Gasto cargado correctamente. Podés cargar otro.')
            return redirect(reverse('expense-create'))

        messages.error(request, 'Revisá los campos.')
        return render(request, self.template_name, {'form': form, 'rform': ReceiptForm()})


# --- Filtro compartido (lista + export) ---
def _filtered_queryset(request):
    """
    Aplica los mismos filtros que la lista y respeta permisos:
    - start / end (YYYY-MM-DD)
    - project (id)
    - user (id) solo para managers
    - operadores ven solo lo propio; anónimo no ve nada
    """
    qs = (
        Expense.objects
        .select_related('project', 'created_by')
        .prefetch_related('receipts')
        .order_by('-date', '-id')
    )

    form = ExpenseFilterForm(request.GET or None, user=request.user)

    if form.is_valid():
        start = form.cleaned_data.get('start')
        end = form.cleaned_data.get('end')
        project = form.cleaned_data.get('project')
        user_obj = form.cleaned_data.get('user')

        if start:
            qs = qs.filter(date__gte=start)
        if end:
            qs = qs.filter(date__lte=end)
        if project:
            qs = qs.filter(project=project)

        if is_manager(request.user):
            if user_obj:
                qs = qs.filter(created_by=user_obj)
        else:
            if request.user.is_authenticated:
                qs = qs.filter(created_by=request.user)
            else:
                qs = qs.none()
    else:
        # Sin form válido, aplicamos visibilidad básica
        if request.user.is_authenticated and not is_manager(request.user):
            qs = qs.filter(created_by=request.user)
        elif not request.user.is_authenticated:
            qs = qs.none()

    return qs, form


# --- Listado ---
class ExpenseListView(LoginRequiredMixin, ListView):  # ⬅️ NEW: requiere login para ver la lista
    model = Expense
    template_name = 'expenses/expense_list.html'
    context_object_name = 'expenses'
    paginate_by = 20
    ordering = ['-date', '-id']

    def get_queryset(self):
        # Guardamos para reusar en el contexto sin recalcular
        self._qs, self._form = _filtered_queryset(self.request)
        return self._qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Usamos lo ya calculado en get_queryset()
        if not hasattr(self, '_form'):
            _, self._form = _filtered_queryset(self.request)
        ctx['filter_form'] = self._form
        ctx['is_manager'] = is_manager(self.request.user)
        return ctx


# --- Export ZIP (respeta los mismos filtros/permiso que la lista) ---
@login_required  # ⬅️ NEW: requiere login para exportar
def export_zip(request):
    qs, form = _filtered_queryset(request)
    buf = build_export(qs)

    # Nombre de archivo amigable: usuario / periodo
    who = "ALL"
    if is_manager(request.user):
        u = form.cleaned_data.get('user') if form.is_valid() else None
        if u:
            who = u.username
    elif request.user.is_authenticated:
        who = request.user.username

    start = form.cleaned_data.get('start') if form.is_valid() else None
    end = form.cleaned_data.get('end') if form.is_valid() else None
    period = (
        f"{start.isoformat() if start else ''}_to_{end.isoformat() if end else ''}".strip('_')
        or 'all'
    )

    fname = f"absl-expenses-{who}-{period}.zip".replace('..', '.')
    resp = HttpResponse(buf.getvalue(), content_type='application/zip')
    resp['Content-Disposition'] = f'attachment; filename=\"{fname}\"'
    return resp
