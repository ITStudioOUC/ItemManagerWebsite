import os
import threading
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import FinancialRecord, Department, Category, ProofImage
from .serializers import (
    FinancialRecordWriteSerializer,
    FinancialRecordReadSerializer,
    DepartmentSerializer,
    CategorySerializer,
    ProofImageSerializer
)

class FinancialRecordViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows financial records to be viewed or edited.
    """
    queryset = FinancialRecord.objects.all()

    def get_serializer_class(self):
        """根据操作类型返回不同的序列化器"""
        if self.action in ['list', 'retrieve']:
            return FinancialRecordReadSerializer
        return FinancialRecordWriteSerializer

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

    def destroy(self, request, *args, **kwargs):
        """删除方法，删除并发送邮件通知"""
        instance = self.get_object()

        # 获取记录信息用于邮件通知
        record_id = instance.id
        record_info = {
            'title': instance.title,
            'amount': str(instance.amount),
            'description': instance.description,
            'record_type': instance.record_type,
            'transaction_date': str(instance.transaction_date),
            'department': instance.department.name if instance.department else '',
            'category': instance.category.name if instance.category else '',
            'fund_manager': instance.fund_manager if hasattr(instance, 'fund_manager') else ''
        }

        # 删除关联的凭证图片文件
        proof_images = ProofImage.objects.filter(financial_record=instance)
        for proof_image in proof_images:
            if proof_image.image:
                try:
                    file_path = proof_image.image.path
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f"成功删除凭证文件 {file_path}")
                except (ValueError, AttributeError, OSError) as e:
                    print(f"删除凭证文件失败 {e}")

        # 立即删除财务记录（会级联删除相关的凭证图片记录）
        super().destroy(request, *args, **kwargs)

        # 异步发送删除通知邮件
        def send_delete_notification():
            """异步发送删除通知邮件"""
            try:
                from email_notice.services import EmailNotificationService

                # 获取用户信息
                user_info = self._get_user_info(request)

                # 构建邮件通知数据
                notification_data = {
                    'id': record_id,
                    'title': f"[已删除] {record_info['title']}",
                    'amount': record_info['amount'],
                    'record_type': record_info['record_type'],
                    'description': record_info['description'],
                    'department': record_info['department'],
                    'category': record_info['category'],
                    'fund_manager': record_info['fund_manager'],
                    'transaction_date': record_info['transaction_date'],
                    'deleted_at': timezone.now().isoformat(),
                    'operation_path': request.path,
                    'operation_method': request.method
                }

                # 发送删除通知邮件
                EmailNotificationService.send_operation_notification(
                    'DELETE', '财务记录', notification_data, user_info
                )
                print(f"删除通知邮件已发送: 财务记录 ID:{record_id}, 标题:{record_info['title']}")

            except Exception as e:
                print(f"发送删除通知邮件失败: {e}")

        # 启动异步邮件发送线程
        email_thread = threading.Thread(target=send_delete_notification)
        email_thread.daemon = True
        email_thread.start()

        # 返回删除成功响应
        return Response({
            'message': f'财务记录 "{record_info["title"]}" 已成功删除，删除通知邮件正在发送',
            'deleted_record_info': record_info
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def upload_images(self, request, pk=None):
        """为财务记录上传多张凭证图片"""
        record = self.get_object()
        files = request.FILES.getlist('images')

        if not files:
            return Response({'error': '没有接收到图片文件'}, status=status.HTTP_400_BAD_REQUEST)

        created_images = []
        for file in files:
            proof_image = ProofImage.objects.create(
                financial_record=record,
                image=file,
                description=request.data.get('description', '')
            )
            created_images.append(ProofImageSerializer(proof_image).data)

        return Response({
            'message': f'成功上传 {len(created_images)} 张图片',
            'images': created_images
        }, status=status.HTTP_201_CREATED)


class ProofImageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows proof images to be viewed or edited.
    """
    queryset = ProofImage.objects.all()
    serializer_class = ProofImageSerializer

    def destroy(self, request, *args, **kwargs):
        """重写删除方法，确保删除图片记录时同时删除物理文件"""
        instance = self.get_object()

        # 获取文件路径
        file_path = None
        if instance.image:
            try:
                file_path = instance.image.path
            except (ValueError, AttributeError):
                # 如果文件路径无效或文件不存在，只删除数据库记录
                pass

        # 删除数据库记录
        super().destroy(request, *args, **kwargs)

        # 删除物理文件
        if file_path and os.path.isfile(file_path):
            try:
                os.remove(file_path)
                print(f"成功删除文件: {file_path}")
            except OSError as e:
                print(f"删除文件失败: {file_path}, 错误: {e}")
                # 即使文件删除失败，也不抛出异常，因为数据库记录已经删除

        return Response({'message': '图片删除成功'}, status=status.HTTP_200_OK)


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows departments to be viewed or edited.
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows categories to be viewed or edited.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
