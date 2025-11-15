from rest_framework import serializers
from django.db.models import Sum, Count, Q

from .models import EvaluationRecord


class EvaluationRecordSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    personnel_name = serializers.CharField(source='personnel', read_only=True)

    def validate_department(self, value):
        """验证部门字段"""
        if value is None:
            raise serializers.ValidationError('部门不能为空')
        if isinstance(value, dict):
            raise serializers.ValidationError('部门必须是一个有效的ID，不能是对象')
        return value

    class Meta:
        model = EvaluationRecord
        fields = [
            'id', 'department', 'department_name', 'personnel', 'personnel_name', 'grade',
            'item_description', 'bonus_score', 'deduction_score', 'remarks',
            'total_score', 'evaluation_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_score', 'created_at', 'updated_at']


class PersonnelSummarySerializer(serializers.Serializer):
    """人员汇总序列化器"""
    personnel = serializers.CharField()
    department_name = serializers.CharField()
    grade = serializers.CharField()
    total_bonus = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_deduction = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_score = serializers.DecimalField(max_digits=10, decimal_places=2)
    bonus_count = serializers.IntegerField()
    deduction_count = serializers.IntegerField()

