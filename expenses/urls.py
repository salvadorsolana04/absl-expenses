from django.urls import path
from .views import ExpenseCreateView, ExpenseListView, export_zip
from .views import delete_expense, bulk_delete_expenses

urlpatterns = [
    path('', ExpenseCreateView.as_view(), name='expense-create'),
    path('gastos/', ExpenseListView.as_view(), name='expense-list'),
    path('export/zip/', export_zip, name='export-zip'),
    
    path('gastos/<int:pk>/delete/', delete_expense, name='expense-delete'),
    path('gastos/bulk-delete/', bulk_delete_expenses, name='expense-bulk-delete'), 
]
