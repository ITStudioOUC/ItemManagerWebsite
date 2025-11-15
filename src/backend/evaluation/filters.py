import django_filters
from finance.models import Department
from personnel.models import Personnel

from .models import EvaluationRecord


class EvaluationRecordFilter(django_filters.FilterSet):
    department = django_filters.ModelChoiceFilter(
        queryset=Department.objects.all(),
        field_name='department',
        label='部门'
    )
    personnel = django_filters.ModelChoiceFilter(
        queryset=Personnel.objects.all(),
        field_name='personnel',
        label='人员'
    )
    date_from = django_filters.DateFilter(
        field_name='evaluation_date',
        lookup_expr='gte',
        label='开始日期'
    )
    date_to = django_filters.DateFilter(
        field_name='evaluation_date',
        lookup_expr='lte',
        label='结束日期'
    )

    class Meta:
        model = EvaluationRecord
        fields = ['department', 'personnel', 'evaluation_date']

