import django_filters
from finance.models import Department

from .models import EvaluationRecord


class EvaluationRecordFilter(django_filters.FilterSet):
    department = django_filters.ModelChoiceFilter(
        queryset=Department.objects.all(),
        field_name='department',
        label='部门'
    )
    personnel = django_filters.CharFilter(
        field_name='personnel',
        lookup_expr='icontains',
        label='人员'
    )
    grade = django_filters.CharFilter(
        field_name='grade',
        lookup_expr='icontains',
        label='年级'
    )

    class Meta:
        model = EvaluationRecord
        fields = ['department', 'personnel', 'grade']

