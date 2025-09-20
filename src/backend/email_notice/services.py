import json
import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)

# 英文key到中文标签的映射
LABEL_MAP = {
    # 通用
    'id': 'ID',
    'title': '标题',
    'name': '名称',
    'description': '描述',
    'status': '状态',
    'category': '类别',
    'owner': '所有者',
    'value': '价值',
    'location': '位置',
    'timestamp': '时间',
    'operation_type': '操作说明',
    'message': '说明',
    'created_at': '创建时间',
    'updated_at': '更新时间',

    # 物品
    'serial_number': '序列号',
    'item_name': '物品名称',
    'item_serial': '物品序列号',
    'user': '使用者',
    'borrower_contact': '使用者联系方式',
    'start_time': '开始时间',
    'end_time': '结束时间',
    'purpose': '使用目的',
    'notes': '备注',
    'is_returned': '是否已归还',
    'condition_before': '使用前状况',
    'condition_after': '使用后状况',
    'purchase_date': '购买日期',
    'expected_return_time': '预计归还时间',

    # 财务记录
    'amount': '金额',
    'transaction_type': '交易类型',
    'transaction_date': '交易日期',
    'record_type': '记录类型',
    'approver': '批准人',
    'department': '部门',
    'department_name': '部门',
    'category_name': '类别',

    # 凭证
    'record_id': '记录ID',
    'record_title': '记录标题',
    'record_amount': '记录金额',
    'uploaded_images_count': '上传图片数量',
    'proof_id': '凭证ID',
    'image_description': '凭证说明',

    # 人员
    'student_id': '学号',
    'gender': '性别',
    'grade_major': '年级专业',
    'project_group': '项目组',
    'project_group_name': '项目组',
    'position': '职位',
    'start_date': '开始日期',
    'end_date': '结束日期',
    'is_active': '是否在任',
    'phone': '电话',
    'qq': 'QQ',
    'email': '邮箱',
    'grader_major': '年级专业',
}

# 这些key为元信息，不参与详情表格展示
META_KEYS = {
    'timestamp', 'operation_path', 'operation_method'
}


def _format_value(value):
    """将值格式化为字符串，布尔/数字/对象友好显示。"""
    if value is None:
        return ''
    # 保留数值0
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, bool):
        return '是' if value else '否'
    if isinstance(value, (list, dict)):
        try:
            return json.dumps(value, ensure_ascii=False)
        except Exception:
            return str(value)
    # 其他转为字符串并去除首尾空白
    return str(value).strip()


def _build_data_items(instance_data: dict):
    """从实例数据构建用于模板的条目列表，空值条目将被过滤。"""
    items = []
    for key, raw in (instance_data or {}).items():
        if key in META_KEYS:
            continue
        label = LABEL_MAP.get(key, key)
        value = _format_value(raw)
        if value == '':
            continue  # 跳过空值
        items.append({'label': label, 'value': value})
    return items


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
        发送操作通知邮件到多个邮箱（带HTML模板，按label显示，空值隐藏）。
        """
        try:
            settings_data = EmailNotificationService.get_notification_settings()

            if not settings_data.get('email_enabled') or not settings_data.get('notification_emails'):
                return

            notification_emails = settings_data.get('notification_emails', [])
            if not notification_emails:
                logger.warning("没有配置启用的通知邮箱")
                return

            # 操作类型映射
            operation_map = {
                'CREATE': '创建',
                'UPDATE': '更新',
                'DELETE': '删除'
            }
            operation_text = operation_map.get(operation_type, operation_type)

            # 可选的操作说明（如：凭证上传/凭证删除/记录更新等）
            operation_hint = _format_value((instance_data or {}).get('operation_type'))

            # 构建模板数据项（排除meta/空值并做label映射）
            data_items = _build_data_items(instance_data)

            # 标题
            subject = f"[爱特工作室管理系统] {model_name}{operation_text}通知"

            # 渲染HTML模板
            context = {
                'model_name': model_name,
                'operation_text': operation_text,
                'operation_hint': operation_hint,
                'timestamp': (instance_data or {}).get('timestamp', ''),
                'user_info': user_info or '系统',
                'data_items': data_items,
            }
            html_body = render_to_string('email_notification.html', context)

            # 构建纯文本降级内容
            plain_lines = [
                f"【{model_name}】{operation_text}通知",
                f"数据类型: {model_name}",
            ]
            if operation_hint:
                plain_lines.append(f"操作说明: {operation_hint}")
            plain_lines.extend([
                f"操作时间: {context['timestamp'] or '未知'}",
                f"操作用户: {context['user_info']}",
                "",
                "变更详情:",
            ])
            for it in data_items:
                plain_lines.append(f"- {it['label']}: {it['value']}")
            plain_lines.append("\n此邮件由爱特工作室物品管理及财务管理系统自动发送")
            plain_message = "\n".join(plain_lines)

            # 发送邮件到所有启用的通知邮箱
            for email in notification_emails:
                if email and str(email).strip():  # 确保邮箱不为空
                    try:
                        send_mail(
                            subject=subject,
                            message=plain_message,
                            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER),
                            recipient_list=[str(email).strip()],
                            fail_silently=False,
                            html_message=html_body,
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
            emails_data: 邮箱数据列表，格式：[{"email": "xxx@xxx.com", 'is_enabled': True, 'description': '描述'}]
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
        except ObjectDoesNotExist:
            logger.error(f"邮箱ID {email_id} 不存在")
            return False
        except Exception as e:
            logger.error(f"更新邮箱状态失败: {e}")
            return False
