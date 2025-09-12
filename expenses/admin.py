from django.contrib import admin
from .models import Expense, Receipt, Project


class ReceiptInline(admin.TabularInline):
    model = Receipt
    extra = 0
    readonly_fields = ("uploaded_at",)
    fields = ("image", "original_name", "uploaded_at")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name", "active")
    search_fields = ("code", "name")
    list_filter = ("active",)
    ordering = ("code", "name")


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        "id", "date", "vendor", "category", "amount",
        "payment_method", "project", "created_by", "created_at", "receipts_count",
    )
    search_fields = (
        "vendor", "description", "project_code", "category",
        "created_by__username", "project__name", "project__code",
    )
    list_filter = ("payment_method", "category", "date", "project", "created_by")
    date_hierarchy = "date"
    ordering = ("-date", "-id")
    readonly_fields = ("created_at",)
    inlines = [ReceiptInline]
    list_select_related = ("project", "created_by")

    @admin.display(description="Recibos")
    def receipts_count(self, obj):
        return obj.receipts.count()


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ("id", "expense", "image", "original_name", "uploaded_at")
    search_fields = ("original_name", "expense__vendor")
    list_filter = ("uploaded_at",)
    readonly_fields = ("uploaded_at",)
