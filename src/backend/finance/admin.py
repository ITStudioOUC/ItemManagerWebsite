from django.contrib import admin
from .models import Department, Category, FinancialRecord, ProofImage


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(ProofImage)
class ProofImageAdmin(admin.ModelAdmin):
    list_display = ['financial_record', 'image', 'description', 'uploaded_at']
    list_filter = ['uploaded_at', 'financial_record']
    search_fields = ['description', 'financial_record__title']
    readonly_fields = ['uploaded_at']


@admin.register(FinancialRecord)
class FinancialRecordAdmin(admin.ModelAdmin):
    list_display = ['title', 'amount', 'record_type', 'transaction_date', 'department', 'category']
    list_filter = ['record_type', 'department', 'category', 'transaction_date']
    search_fields = ['title', 'description']
    date_hierarchy = 'transaction_date'
