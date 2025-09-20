from django.contrib import admin

from .models import Personnel, ProjectGroup


@admin.register(ProjectGroup)
class ProjectGroupAdmin(admin.ModelAdmin):
    """项目组管理"""
    list_display = ['name', 'department', 'description', 'created_at']
    list_filter = ['department', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['department', 'name']

import django_filters
@admin.register(Personnel)
class PersonnelAdmin(admin.ModelAdmin):
    """人员信息管理"""
    list_display = [
        'name', 'student_id', 'department', 'project_group', 'position',
        'is_active', 'start_date', 'end_date'
    ]
    list_filter = [
        'department', 'project_group', 'position', 'gender',
        'is_active', 'start_date'
    ]
    search_fields = ['name', 'student_id', 'phone', 'email', 'grade_major']
    ordering = ['-is_active', 'department', 'position', 'name']

    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'student_id', 'gender', 'grade_major')
        }),
        ('职位信息', {
            'fields': ('department', 'project_group', 'position', 'start_date', 'end_date', 'is_active')
        }),
        ('联系方式', {
            'fields': ('phone', 'qq', 'email')
        }),
        ('其他信息', {
            'fields': ('description',),
            'classes': ('collapse',)
        })
    )

    readonly_fields = ('created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        """保存模型时的额外处理"""
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """优化查询"""
        return super().get_queryset(request).select_related('department', 'project_group')
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
