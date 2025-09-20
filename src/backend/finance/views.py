import os
import threading

from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

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
    获取财务记录
    """
    authentication_classes = [JWTAuthentication]
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
            'timestamp': timezone.now().isoformat(),
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
                    'timestamp': timezone.now().isoformat(), # 删除条目的时间 :(
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

        # 异步发送凭证上传通知邮件
        def send_proof_upload_notification():
            try:
                from email_notice.services import EmailNotificationService

                user_info = self._get_user_info(request)

                # 构建凭证更新通知数据
                notification_data = {
                    'record_id': record.id,
                    'record_title': record.title,
                    'record_amount': str(record.amount),
                    'uploaded_images_count': len(created_images),
                    'timestamp': timezone.now().isoformat(),
                    'operation_type': '凭证上传',
                    'operation_path': request.path,
                    'operation_method': request.method
                }

                # 发送凭证更新通知
                EmailNotificationService.send_operation_notification(
                    'UPDATE', '财务凭证', notification_data, user_info
                )
                print(f"凭证上传通知邮件已发送: 财务记录 ID:{record.id}, 上传{len(created_images)}张图片")

            except Exception as e:
                print(f"发送凭证上传通知邮件失败: {e}")

        # 启动异步邮件发送线程
        email_thread = threading.Thread(target=send_proof_upload_notification)
        email_thread.daemon = True
        email_thread.start()

        return Response({
            'message': f'成功上传 {len(created_images)} 张图片',
            'images': created_images
        }, status=status.HTTP_201_CREATED)


class ProofImageViewSet(viewsets.ModelViewSet):
    """
    凭证API
    """
    authentication_classes = [JWTAuthentication]
    queryset = ProofImage.objects.all()
    serializer_class = ProofImageSerializer

    def destroy(self, request, *args, **kwargs):
        """删除方法，确保删除图片记录时同时删除物理文件，并发送邮件通知"""
        instance = self.get_object()

        # 获取凭证信息用于邮件通知
        proof_info = {
            'id': instance.id,
            'record_id': instance.financial_record.id,
            'record_title': instance.financial_record.title,
            'record_amount': str(instance.financial_record.amount),
            'image_description': instance.description,
            'timestamp': timezone.now().isoformat(),
        }

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

        # 异步发送凭证删除通知邮件
        def send_proof_delete_notification():
            try:
                from email_notice.services import EmailNotificationService

                user_info = self._get_user_info(request)

                # 构建凭证删除通知数据
                notification_data = {
                    'proof_id': proof_info['id'],
                    'record_id': proof_info['record_id'],
                    'record_title': proof_info['record_title'],
                    'record_amount': proof_info['record_amount'],
                    'image_description': proof_info['image_description'],
                    'timestamp': proof_info['timestamp'],
                    'operation_type': '凭证删除',
                    'operation_path': request.path,
                    'operation_method': request.method
                }

                # 发送凭证删除通知
                EmailNotificationService.send_operation_notification(
                    'DELETE', '财务凭证', notification_data, user_info
                )
                print(f"凭证删除通知邮件已发送: 财务记录 ID:{proof_info['record_id']}, 凭证 ID:{proof_info['id']}")

            except Exception as e:
                print(f"发送凭证删除通知邮件失败: {e}")

        # 启动异步邮件发送线程
        email_thread = threading.Thread(target=send_proof_delete_notification)
        email_thread.daemon = True
        email_thread.start()

        return Response({'message': '图片删除成功'}, status=status.HTTP_200_OK)

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


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    获取部门
    """
    authentication_classes = [JWTAuthentication]
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    def destroy(self, request, *args, **kwargs):
        """删除部门，发送邮件通知"""
        from email_notice.services import EmailNotificationService
        import threading
        import logging

        logger = logging.getLogger(__name__)

        # 获取要删除的部门信息
        department = self.get_object()
        department_data = {
            'id': department.id,
            'name': department.name,
        }

        # 获取用户信息
        user_info = self._get_user_info(request)

        # 执行删除操作
        response = super().destroy(request, *args, **kwargs)

        # 异步发送删除通知邮件
        def send_delete_notification():
            try:
                EmailNotificationService.send_operation_notification(
                    'DELETE', '部门', department_data, user_info
                )
            except Exception as e:
                logger.error(f"发送部门删除通知邮件失败: {e}")

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


class CategoryViewSet(viewsets.ModelViewSet):
    """
    获取分类
    """
    authentication_classes = [JWTAuthentication]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
