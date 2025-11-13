from rest_framework import serializers

from .models import EvaluationRecord


class EvaluationRecordSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    personnel_name = serializers.CharField(source='personnel.name', read_only=True)

    class Meta:
        model = EvaluationRecord
        fields = [
            'id', 'department', 'department_name', 'personnel', 'personnel_name',
            'item_description', 'bonus_score', 'deduction_score', 'remarks',
            'total_score', 'evaluation_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['total_score', 'created_at', 'updated_at']

