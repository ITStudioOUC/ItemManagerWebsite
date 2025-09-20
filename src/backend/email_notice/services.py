from django.core.mail import send_mail
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)

class EmailNotificationService:
    """邮件通知服务"""

    @staticmethod
    def get_notification_settings():
        """获取通知设置"""
        try:
            from .models import NotificationEmail, NotificationSettings

            # 获取全局设置
            global_settings = NotificationSettings.get_settings()

            # 获取启用的邮箱列表
            enabled_emails = NotificationEmail.objects.filter(is_enabled=True).values_list('email', flat=True)

            return {
                'email_enabled': global_settings.email_notification_enabled,
                'notification_emails': list(enabled_emails)
            }
        except Exception as e:
            logger.error(f"获取通知设置失败: {e}")
            return {'email_enabled': False, 'notification_emails': []}

    @staticmethod
    def send_operation_notification(operation_type, model_name, instance_data, user_info=None):
        """
        发送操作通知邮件到多个邮箱

        Args:
            operation_type: 操作类型 ('CREATE', 'UPDATE', 'DELETE')
            model_name: 模型名称 (如 'Item', 'FinanceRecord')
            instance_data: 实例数据
            user_info: 操作用户信息
        """
        try:
            settings_data = EmailNotificationService.get_notification_settings()

            if not settings_data.get('email_enabled') or not settings_data.get('notification_emails'):
                return

            notification_emails = settings_data.get('notification_emails', [])
            if not notification_emails:
                logger.warning("没有配置启用的通知邮箱")
                return

            # 构建邮件内容
            subject = f"[爱特工作室管理系统] {model_name}数据变更通知"

            operation_map = {
                'CREATE': '创建',
                'UPDATE': '更新',
                'DELETE': '删除'
            }

            operation_text = operation_map.get(operation_type, operation_type)

            message = f"""
                系统数据变更通知
                
                操作类型: {operation_text}
                数据类型: {model_name}
                操作时间: {instance_data.get('timestamp', '未知')}
                操作用户: {user_info or '系统'}
                
                变更详情:
                {json.dumps(instance_data, ensure_ascii=False, indent=2)}
                
                ---
                此邮件由爱特工作室物品管理及财务管理系统自动发送
            """

            # 发送邮件到所有启用的通知邮箱
            for email in notification_emails:
                if email.strip():  # 确保邮箱不为空
                    try:
                        send_mail(
                            subject=subject,
                            message=message,
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=[email.strip()],
                            fail_silently=False,
                        )
                        logger.info(f"邮件通知发送成功到 {email}: {operation_type} {model_name}")
                    except Exception as e:
                        logger.error(f"发送邮件到 {email} 失败: {e}")

        except Exception as e:
            logger.error(f"发送邮件通知失败: {e}")

    @staticmethod
    def send_item_operation_notification(operation_type, item_instance, user_info=None):
        """发送物品操作通知"""
        try:
            instance_data = {
                'id': getattr(item_instance, 'id', None),
                'name': getattr(item_instance, 'name', ''),
                'serial_number': getattr(item_instance, 'serial_number', ''),
                'status': getattr(item_instance, 'status', ''),
                'category': getattr(item_instance, 'category', ''),
                'owner': getattr(item_instance, 'owner', ''),
                'timestamp': str(getattr(item_instance, 'updated_at', '')),
            }

            EmailNotificationService.send_operation_notification(
                operation_type, '物品', instance_data, user_info
            )
        except Exception as e:
            logger.error(f"发送物品操作通知失败: {e}")

    @staticmethod
    def send_finance_operation_notification(operation_type, finance_instance, user_info=None):
        """发送财务记录操作通知"""
        try:
            instance_data = {
                'id': getattr(finance_instance, 'id', None),
                'amount': str(getattr(finance_instance, 'amount', '')),
                'transaction_type': getattr(finance_instance, 'transaction_type', ''),
                'description': getattr(finance_instance, 'description', ''),
                'department': str(getattr(finance_instance, 'department', '')),
                'category': str(getattr(finance_instance, 'category', '')),
                'approver': getattr(finance_instance, 'approver', ''),
                'timestamp': str(getattr(finance_instance, 'transaction_date', '')),
            }

            EmailNotificationService.send_operation_notification(
                operation_type, '财务记录', instance_data, user_info
            )
        except Exception as e:
            logger.error(f"发送财务记录操作通知失败: {e}")

    @staticmethod
    def update_notification_emails(emails_data):
        """
        更新通知邮箱列表（使用数据库存储）

        Args:
            emails_data: 邮箱数据列表，格式：[{'email': 'xxx@xxx.com', 'is_enabled': True, 'description': '描述'}]
        """
        try:
            from .models import NotificationEmail

            # 清空现有邮箱
            NotificationEmail.objects.all().delete()

            # 添加新的邮箱
            for email_info in emails_data:
                if isinstance(email_info, str):
                    # 兼容旧格式（纯邮箱字符串）
                    NotificationEmail.objects.create(
                        email=email_info.strip(),
                        is_enabled=True
                    )
                elif isinstance(email_info, dict):
                    # 新格式（包含详细信息）
                    NotificationEmail.objects.create(
                        email=email_info.get('email', '').strip(),
                        is_enabled=email_info.get('is_enabled', True),
                        description=email_info.get('description', '')
                    )

            logger.info(f"通知邮箱配置已更新: {len(emails_data)} 个邮箱")
            return True
        except Exception as e:
            logger.error(f"更新通知邮箱配置失败: {e}")
            return False

    @staticmethod
    def update_global_notification_setting(enabled):
        """
        更新全局邮件通知开关

        Args:
            enabled: 是否启用邮件通知
        """
        try:
            from .models import NotificationSettings

            settings = NotificationSettings.get_settings()
            settings.email_notification_enabled = enabled
            settings.save()

            logger.info(f"全局邮件通知设置已更新: {enabled}")
            return True
        except Exception as e:
            logger.error(f"更新全局邮件通知设置失败: {e}")
            return False

    @staticmethod
    def get_all_notification_emails():
        """获取所有通知邮箱（包括禁用的）"""
        try:
            from .models import NotificationEmail

            emails = NotificationEmail.objects.all().values(
                'id', 'email', 'is_enabled', 'description', 'created_at', 'updated_at'
            )
            return list(emails)
        except Exception as e:
            logger.error(f"获取通知邮箱列表失败: {e}")
            return []

    @staticmethod
    def toggle_email_status(email_id, is_enabled):
        """
        切换指定邮箱的启用状态

        Args:
            email_id: 邮箱ID
            is_enabled: 是否启用
        """
        try:
            from .models import NotificationEmail

            email_obj = NotificationEmail.objects.get(id=email_id)
            email_obj.is_enabled = is_enabled
            email_obj.save()

            logger.info(f"邮箱 {email_obj.email} 状态已更新: {is_enabled}")
            return True
        except NotificationEmail.DoesNotExist:
            logger.error(f"邮箱ID {email_id} 不存在")
            return False
        except Exception as e:
            logger.error(f"更新邮箱状态失败: {e}")
            return False
