from django.contrib import admin

from .models import Personnel, ProjectGroup


@admin.register(ProjectGroup)
class ProjectGroupAdmin(admin.ModelAdmin):
    """项目组管理"""
    list_display = ['name', 'get_departments', 'description', 'created_at']
    list_filter = ['departments', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    filter_horizontal = ['departments']

    def get_departments(self, obj):
        """获取部门列表显示"""
        return ", ".join([dept.name for dept in obj.departments.all()])
    get_departments.short_description = '所属部门'


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
