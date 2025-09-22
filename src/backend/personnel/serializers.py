from finance.models import Department
from rest_framework import serializers

from .models import Personnel, ProjectGroup


class ProjectGroupSerializer(serializers.ModelSerializer):
    """项目组序列化器"""
    department_names = serializers.ListField(read_only=True)
    departments_info = serializers.SerializerMethodField()

    class Meta:
        model = ProjectGroup
        fields = ['id', 'name', 'departments', 'department_names', 'departments_info', 'description', 'created_at']
        read_only_fields = ['created_at']

    def get_departments_info(self, obj):
        """获取部门详细信息"""
        return [{'id': dept.id, 'name': dept.name} for dept in obj.departments.all()]


class PersonnelReadSerializer(serializers.ModelSerializer):
    """人员信息读取序列化器"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    project_group_name = serializers.CharField(source='project_group.name', read_only=True)
    position_display = serializers.CharField(source='position', read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    status_display = serializers.CharField(read_only=True)

    class Meta:
        model = Personnel
        fields = [
            'id', 'name', 'student_id', 'gender', 'gender_display', 'grade_major',
            'department', 'department_name', 'project_group', 'project_group_name',
            'position', 'position_display', 'start_date', 'end_date', 'is_active',
            'status_display', 'phone', 'qq', 'email', 'description',
            'created_at', 'updated_at'
        ]


class PersonnelWriteSerializer(serializers.ModelSerializer):
    """人员信息写入序列化器"""

    class Meta:
        model = Personnel
        fields = [
            'id', 'name', 'student_id', 'gender', 'grade_major',
            'department', 'project_group', 'position', 'start_date', 'end_date',
            'is_active', 'phone', 'qq', 'email', 'description'
        ]

    def validate_project_group(self, value):
        """验证项目组是否包含选定的部门"""
        if value and hasattr(self, 'initial_data'):
            department_id = self.initial_data.get('department')
            if department_id:
                # 检查项目组的部门列表中是否包含选定的部门
                if not value.departments.filter(id=int(department_id)).exists():
                    raise serializers.ValidationError("项目组必须包含选定的部门")
        return value

    def validate(self, attrs):
        """整体验证"""
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')

        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError({
                'end_date': '任职结束时间必须晚于开始时间'
            })

        return attrs
