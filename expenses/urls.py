from django.urls import path
from .views import ExpenseCreateView, ExpenseListView, export_zip

urlpatterns = [
    path('', ExpenseCreateView.as_view(), name='expense-create'),
    path('gastos/', ExpenseListView.as_view(), name='expense-list'),
    path('export/zip/', export_zip, name='export-zip'),
]
