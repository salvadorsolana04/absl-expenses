from django.contrib import admin
from .models import Expense, Receipt

class ReceiptInline(admin.TabularInline):
    model = Receipt
    extra = 0

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "vendor", "category", "amount", "payment_method")
    search_fields = ("vendor", "description", "project_code", "category")
    list_filter = ("payment_method", "category", "date")
    inlines = [ReceiptInline]

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ("id", "expense", "image", "original_name")
