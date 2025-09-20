from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
import logging
from .models import Personnel, ProjectGroup
from .serializers import (
    PersonnelReadSerializer,
    PersonnelWriteSerializer,
    ProjectGroupSerializer
)
from .filters import PersonnelFilter

logger = logging.getLogger(__name__)


class PersonnelViewSet(viewsets.ModelViewSet):
    """人员信息视图集"""
    queryset = Personnel.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PersonnelFilter
    search_fields = ['name', 'student_id', 'phone', 'email', 'grade_major']
    ordering_fields = ['created_at', 'start_date', 'end_date', 'name']
    ordering = ['-is_active', 'department', 'position', 'name']

    def get_serializer_class(self):
        """根据操作类型返回不同的序列化器"""
        if self.action in ['list', 'retrieve']:
            return PersonnelReadSerializer
        return PersonnelWriteSerializer

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取人员统计信息"""
        total_count = Personnel.objects.count()
        active_count = Personnel.objects.filter(is_active=True).count()
        inactive_count = total_count - active_count

        # 按部门统计
        department_stats = {}
        for person in Personnel.objects.select_related('department'):
            dept_name = person.department.name
            if dept_name not in department_stats:
                department_stats[dept_name] = {'total': 0, 'active': 0, 'inactive': 0}
            department_stats[dept_name]['total'] += 1
            if person.is_active:
                department_stats[dept_name]['active'] += 1
            else:
                department_stats[dept_name]['inactive'] += 1

        # 按职位统计
        position_stats = {}
        for person in Personnel.objects.all():
            position = person.position
            if position not in position_stats:
                position_stats[position] = {'total': 0, 'active': 0, 'inactive': 0}
            position_stats[position]['total'] += 1
            if person.is_active:
                position_stats[position]['active'] += 1
            else:
                position_stats[position]['inactive'] += 1

        return Response({
            'overview': {
                'total': total_count,
                'active': active_count,
                'inactive': inactive_count
            },
            'by_department': department_stats,
            'by_position': position_stats
        })

    @action(detail=True, methods=['post'])
    def set_inactive(self, request, pk=None):
        """设置人员为已卸任状态"""
        personnel = self.get_object()
        personnel.is_active = False
        personnel.end_date = timezone.now().date()
        personnel.save()

        serializer = self.get_serializer(personnel)
        return Response({
            'message': f'{personnel.name} 已设置为已卸任状态',
            'data': serializer.data
        })

    @action(detail=True, methods=['post'])
    def set_active(self, request, pk=None):
        """设置人员为在职状态"""
        personnel = self.get_object()
        personnel.is_active = True
        personnel.end_date = None
        personnel.save()

        serializer = self.get_serializer(personnel)
        return Response({
            'message': f'{personnel.name} 已设置为在职状态',
            'data': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        """删除人员，发送邮件通知"""
        from email_notice.services import EmailNotificationService
        import threading

        # 获取要删除的人员信息
        personnel = self.get_object()
        personnel_data = {
            'id': personnel.id,
            'name': personnel.name,
            'student_id': personnel.student_id,
            'email': personnel.email,
            'phone': personnel.phone,
            'department_name': personnel.department.name if personnel.department else '',
            'project_group_name': personnel.project_group.name if personnel.project_group else '',
            'position': personnel.position,
            'is_active': personnel.is_active,
            'start_date': str(personnel.start_date),
            'end_date': str(personnel.end_date) if personnel.end_date else '',
            'timestamp': timezone.now().isoformat(),

        }

        # 获取用户信息
        user_info = self._get_user_info(request)

        # 执行删除操作
        response = super().destroy(request, *args, **kwargs)

        # 异步发送删除通知邮件
        def send_delete_notification():
            try:
                EmailNotificationService.send_operation_notification(
                    'DELETE', '人员', personnel_data, user_info
                )
            except Exception as e:
                logger.error(f"发送人员删除通知邮件失败: {e}")

        thread = threading.Thread(target=send_delete_notification)
        thread.daemon = True
        thread.start()

        return response

    def _get_user_info(self, request):
        """获取用户信息"""
        try:
            if hasattr(request, 'user') and request.user.is_authenticated:
                return f"{request.user.username} ({request.user.email})"
            else:
                return f"匿名用户 (IP: {self._get_client_ip(request)})"
        except:
            return "未知用户"

    def _get_client_ip(self, request):
        """获取客户端IP"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    @action(detail=False, methods=['post'])
    def check_expired(self, request):
        """检查并更新已到期的人员状态"""
        updated_count, updated_names = Personnel.check_and_update_expired_personnel()

        if updated_count > 0:
            return Response({
                'message': f'成功将 {updated_count} 名人员设置为已卸任状态',
                'updated_personnel': updated_names,
                'count': updated_count
            })
        else:
            return Response({
                'message': '没有需要更新的人员',
                'updated_personnel': [],
                'count': 0
            })


class ProjectGroupViewSet(viewsets.ModelViewSet):
    """项目组视图集"""
    queryset = ProjectGroup.objects.all()
    serializer_class = ProjectGroupSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['department']
    search_fields = ['name', 'description']
    ordering = ['department', 'name']

    @action(detail=False, methods=['get'])
    def by_department(self, request):
        """按部门获取项目组"""
        department_id = request.query_params.get('department_id')
        if department_id:
            project_groups = ProjectGroup.objects.filter(department_id=department_id)
            serializer = self.get_serializer(project_groups, many=True)
            return Response(serializer.data)
        return Response([])

    def destroy(self, request, *args, **kwargs):
        """删除项目组，发送邮件通知"""
        from email_notice.services import EmailNotificationService
        import threading

        # 获取要删除的项目组信息
        project_group = self.get_object()
        project_group_data = {
            'id': project_group.id,
            'name': project_group.name,
            'department_name': project_group.department.name if project_group.department else '',
            'description': project_group.description,
            'created_at': str(project_group.created_at),
            'operation_path': request.path,
            'operation_method': request.method
        }

        # 获取用户信息
        user_info = self._get_user_info(request)

        # 执行删除操作
        response = super().destroy(request, *args, **kwargs)

        # 异步发送删除通知邮件
        def send_delete_notification():
            try:
                EmailNotificationService.send_operation_notification(
                    'DELETE', '项目组', project_group_data, user_info
                )
            except Exception as e:
                logger.error(f"发送项目组删除通知邮件失败: {e}")

        thread = threading.Thread(target=send_delete_notification)
        thread.daemon = True
        thread.start()

        return response

    def _get_user_info(self, request):
        """获取用户信息"""
        try:
            if hasattr(request, 'user') and request.user.is_authenticated:
                return f"{request.user.username} ({request.user.email})"
            else:
                return f"匿名用户 (IP: {self._get_client_ip(request)})"
        except:
            return "未知用户"

    def _get_client_ip(self, request):
        """获取客户端IP"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    @action(detail=False, methods=['get'])
    def by_department(self, request):
        """按部门获取项目组"""
        department_id = request.query_params.get('department_id')
        if department_id:
            project_groups = ProjectGroup.objects.filter(department_id=department_id)
            serializer = self.get_serializer(project_groups, many=True)
            return Response(serializer.data)
        return Response([])
