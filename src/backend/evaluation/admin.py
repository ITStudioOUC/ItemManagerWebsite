from django.contrib import admin

from .models import EvaluationRecord


@admin.register(EvaluationRecord)
class EvaluationRecordAdmin(admin.ModelAdmin):
    list_display = [
        'evaluation_date', 'department', 'personnel', 'item_description',
        'bonus_score', 'deduction_score', 'total_score', 'created_at'
    ]
    list_filter = ['department', 'evaluation_date', 'created_at']
    search_fields = ['personnel', 'item_description', 'remarks']
    ordering = ['-evaluation_date', '-created_at']
