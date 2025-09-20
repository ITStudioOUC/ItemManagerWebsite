import django_filters
from django.db import models
from .models import Personnel, ProjectGroup
from finance.models import Department


class PersonnelFilter(django_filters.FilterSet):
    """人员信息过滤器"""

    # 基本筛选
    department = django_filters.ModelChoiceFilter(
        queryset=Department.objects.all(),
        field_name='department',
        label='部门'
    )

    project_group = django_filters.ModelChoiceFilter(
        queryset=ProjectGroup.objects.all(),
        field_name='project_group',
        label='项目组'
    )

    position = django_filters.CharFilter(
        field_name='position',
        lookup_expr='icontains',
        label='职位'
    )

    gender = django_filters.ChoiceFilter(
        choices=Personnel.GENDER_CHOICES,
        field_name='gender',
        label='性别'
    )

    is_active = django_filters.BooleanFilter(
        field_name='is_active',
        label='在职状态'
    )

    # 日期范围筛选
    start_date_from = django_filters.DateFilter(
        field_name='start_date',
        lookup_expr='gte',
        label='任职开始时间（从）'
    )

    start_date_to = django_filters.DateFilter(
        field_name='start_date',
        lookup_expr='lte',
        label='任职开始时间（到）'
    )

    end_date_from = django_filters.DateFilter(
        field_name='end_date',
        lookup_expr='gte',
        label='任职结束时间（从）'
    )

    end_date_to = django_filters.DateFilter(
        field_name='end_date',
        lookup_expr='lte',
        label='任职结束时间（到）'
    )

    class Meta:
        model = Personnel
        fields = ['department', 'project_group', 'position', 'gender', 'is_active']
