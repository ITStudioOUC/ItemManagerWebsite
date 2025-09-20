from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
import json
import re

from .services import EmailNotificationService


@api_view(["GET", "POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def notification_settings(request):
    """通知设置API（需要JWT）"""

    if request.method == 'GET':
        try:
            settings_data = EmailNotificationService.get_notification_settings()
            all_emails = EmailNotificationService.get_all_notification_emails()
            return Response({
                'success': True,
                'data': {
                    'email_enabled': settings_data.get('email_enabled', False),
                    'notification_emails': settings_data.get('notification_emails', []),
                    'all_emails': all_emails
                }
            })
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)

    elif request.method == 'POST':
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body or '{}')
            emails_to_update = data.get('notification_emails')
            email_enabled_status = data.get('email_enabled')

            # 标志位，用于判断是否执行了任何更新操作
            was_updated = False

            # 1. 如果请求中包含 'notification_emails' 键，则处理邮箱列表
            if emails_to_update is not None:  # 允许空列表
                email_regex = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
                valid_emails_data = []

                for email_info in emails_to_update:
                    # 兼容前端可能发送的字符串或对象格式
                    if isinstance(email_info, str):
                        if email_info.strip() and email_regex.match(email_info.strip()):
                            valid_emails_data.append({
                                'email': email_info.strip(),
                                'is_enabled': True,
                                'description': ''
                            })
                    elif isinstance(email_info, dict):
                        email = email_info.get('email', '').strip()
                        if email and email_regex.match(email):
                            valid_emails_data.append({
                                'email': email,
                                'is_enabled': email_info.get('is_enabled', True),
                                'description': email_info.get('description', '')
                            })

                # 调用服务层更新邮箱，服务层需要能处理空列表
                EmailNotificationService.update_notification_emails(valid_emails_data)
                was_updated = True

            if email_enabled_status is not None:
                EmailNotificationService.update_global_notification_setting(email_enabled_status)
                was_updated = True

            # 执行更新成功，返回成功
            if was_updated:
                return Response({
                    'success': True,
                    'message': '通知设置已更新',
                    # 返回最新的数据状态
                    'data': {
                        'email_enabled': EmailNotificationService.get_notification_settings().get('email_enabled', False),
                        'all_emails': EmailNotificationService.get_all_notification_emails()
                    }
                })
            else:
                # 如果请求体为空或不包含任何有效键，则返回错误
                return Response({'success': False, 'error': '未提供任何有效的更新数据'}, status=400)

        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=500)

    return Response({'success': False, 'error': '不支持的请求方法'}, status=405)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def toggle_email_status(request):
    """切换邮箱启用状态API（需要JWT）"""
    try:
        data = request.data if hasattr(request, 'data') else json.loads(request.body or '{}')
        email_id = data.get('email_id')
        is_enabled = data.get('is_enabled', True)

        if not email_id:
            return Response({'success': False, 'error': '缺少邮箱ID'}, status=400)

        success = EmailNotificationService.toggle_email_status(email_id, is_enabled)

        if success:
            return Response({
                'success': True,
                'message': f'邮箱状态已更新为{"启用" if is_enabled else "禁用"}',
                'data': {
                    'all_emails': EmailNotificationService.get_all_notification_emails()
                }
            })
        else:
            return Response({'success': False, 'error': '更新邮箱状态失败'}, status=500)

    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)
