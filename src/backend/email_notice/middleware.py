from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from .services import EmailNotificationService
import json
import logging
import threading
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)

class EmailNotificationMiddleware(MiddlewareMixin):
    """邮件通知中间件"""

    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
        # 用于存储删除前的数据
        self._delete_data_cache = {}

    def process_request(self, request):
        """在处理请求前，如果是删除操作，先获取要删除的数据"""
        try:
            # 只处理DELETE操作
            if request.method != 'DELETE':
                return None

            # 只处理API请求
            if not request.path.startswith('/api/'):
                return None

            # 从URL路径中提取ID
            path_parts = request.path.split('/')
            record_id = None
            for part in path_parts:
                if part.isdigit():
                    record_id = part
                    break

            if not record_id:
                return None

            # 根据路径类型获取对应的数据
            if '/api/items/' in request.path:
                data = self._get_item_data_before_delete(record_id)
                if data:
                    self._delete_data_cache[f"item_{record_id}"] = data
            elif '/api/records/' in request.path or '/api/finance/' in request.path:
                data = self._get_finance_data_before_delete(record_id)
                if data:
                    self._delete_data_cache[f"finance_{record_id}"] = data

        except Exception as e:
            logger.error(f"获取删除前数据失败: {e}")

        return None

    def _get_item_data_before_delete(self, item_id):
        """获取物品删除前的数据"""
        try:
            from items.models import Item
            item = Item.objects.get(id=item_id)
            return {
                'id': item.id,
                'name': item.name,
                'serial_number': item.serial_number,
                'status': item.status,
                'category': item.category,
                'owner': item.owner,
                'purchase_date': str(item.purchase_date) if item.purchase_date else '',
                'purchase_price': str(item.purchase_price) if item.purchase_price else '',
                'description': item.description,
                'updated_at': str(item.updated_at) if hasattr(item, 'updated_at') else '',
            }
        except Exception as e:
            logger.error(f"获取物品数据失败: {e}")
            return None

    def _get_finance_data_before_delete(self, record_id):
        """获取财务记录删除前的数据"""
        try:
            from finance.models import FinanceRecord
            record = FinanceRecord.objects.get(id=record_id)
            return {
                'id': record.id,
                'amount': str(record.amount),
                'transaction_type': record.transaction_type,
                'description': record.description,
                'department': record.department.name if record.department else '',
                'category': record.category.name if record.category else '',
                'approver': record.approver,
                'transaction_date': str(record.transaction_date),
                'proof_images': [str(img.image) for img in record.proof_images.all()] if hasattr(record, 'proof_images') else []
            }
        except Exception as e:
            logger.error(f"获取财务记录数据失败: {e}")
            return None

    def process_response(self, request, response):
        """处理响应，在数据修改操作成功后异步发送邮件通知"""
        try:
            # 只处理API请求
            if not request.path.startswith('/api/'):
                return response

            # 只处理数据修改操作
            if request.method not in ['POST', 'PUT', 'PATCH', 'DELETE']:
                return response

            # 只处理成功的响应
            if not (200 <= response.status_code < 300):
                return response

            # 获取用户信息
            user_info = self._get_user_info(request)

            # 异步处理邮件通知，避免阻塞API响应
            if '/api/items/' in request.path:
                self._handle_item_operation_async(request, response, user_info)
            elif '/api/records/' in request.path or '/api/finance/' in request.path:
                self._handle_finance_operation_async(request, response, user_info)

        except Exception as e:
            logger.error(f"邮件通知中间件处理失败: {e}")

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

    def _handle_item_operation_async(self, request, response, user_info):
        """异步处理物品操作"""
        def send_notification():
            try:
                operation_type = self._get_operation_type(request.method, request.path)

                # 对于DELETE操作，使用预先获取的数据
                if request.method == 'DELETE':
                    # 从URL路径中提取ID
                    path_parts = request.path.split('/')
                    item_id = None
                    for part in path_parts:
                        if part.isdigit():
                            item_id = part
                            break

                    # 尝试从缓存中获取删除前的数据
                    cached_data = self._delete_data_cache.get(f"item_{item_id}")
                    if cached_data:
                        notification_data = {
                            'id': cached_data.get('id', item_id),
                            'name': f"[已删除] {cached_data.get('name', '未知物品')}",
                            'serial_number': cached_data.get('serial_number', ''),
                            'status': f"[删除前状态: {cached_data.get('status', '未知')}]",
                            'category': cached_data.get('category', ''),
                            'owner': cached_data.get('owner', ''),
                            'purchase_date': cached_data.get('purchase_date', ''),
                            'purchase_price': cached_data.get('purchase_price', ''),
                            'description': f"删除前描述: {cached_data.get('description', '')}",
                            'timestamp': cached_data.get('updated_at', ''),
                            'operation_path': request.path,
                            'operation_method': request.method
                        }
                else:
                    # 尝试从响应中获取数据
                    if hasattr(response, 'data'):
                        item_data = response.data
                    else:
                        try:
                            content = response.content.decode('utf-8')
                            item_data = json.loads(content) if content else {}
                        except:
                            item_data = {}

                    # 确保item_data不为None
                    if item_data is None:
                        item_data = {}

                    # 构建通知数据
                    notification_data = {
                        'id': item_data.get('id', ''),
                        'name': item_data.get('name', ''),
                        'serial_number': item_data.get('serial_number', ''),
                        'status': item_data.get('status', ''),
                        'category': item_data.get('category', ''),
                        'owner': item_data.get('owner', ''),
                        'timestamp': item_data.get('updated_at', ''),
                        'operation_path': request.path,
                        'operation_method': request.method
                    }

                EmailNotificationService.send_operation_notification(
                    operation_type, '物品', notification_data, user_info
                )

            except Exception as e:
                logger.error(f"异步处理物品操作通知失败: {e} 如果需要查看删除前的数据，请检查以前的邮件。")

        # 创建并启动后台线程
        thread = threading.Thread(target=send_notification)
        thread.daemon = True  # 设置为守护线程
        thread.start()

    def _handle_finance_operation_async(self, request, response, user_info):
        """异步处理财务操作"""
        def send_notification():
            try:
                operation_type = self._get_operation_type(request.method, request.path)

                # 对于DELETE操作，响应通常不包含数据，需要从URL路径中提取ID
                if request.method == 'DELETE':
                    # 从URL路径中提取ID
                    path_parts = request.path.split('/')
                    record_id = None
                    for part in path_parts:
                        if part.isdigit():
                            record_id = part
                            break

                    notification_data = {
                        'id': record_id or '未知',
                        'amount': '已删除记录',
                        'transaction_type': '已删除',
                        'description': '财务记录已被删除',
                        'department': '未知',
                        'category': '未知',
                        'approver': '未知',
                        'timestamp': '删除时间未知',
                        'operation_path': request.path,
                        'operation_method': request.method
                    }
                else:
                    # 尝试从响应中获取数据
                    if hasattr(response, 'data'):
                        finance_data = response.data
                    else:
                        try:
                            content = response.content.decode('utf-8')
                            finance_data = json.loads(content) if content else {}
                        except:
                            finance_data = {}

                    # 确保finance_data不为None
                    if finance_data is None:
                        finance_data = {}

                    # 构建通知数据
                    notification_data = {
                        'id': finance_data.get('id', ''),
                        'amount': finance_data.get('amount', ''),
                        'transaction_type': finance_data.get('transaction_type', ''),
                        'description': finance_data.get('description', ''),
                        'department': finance_data.get('department', ''),
                        'category': finance_data.get('category', ''),
                        'approver': finance_data.get('approver', ''),
                        'timestamp': finance_data.get('transaction_date', ''),
                        'operation_path': request.path,
                        'operation_method': request.method
                    }

                EmailNotificationService.send_operation_notification(
                    operation_type, '财务记录', notification_data, user_info
                )

            except Exception as e:
                logger.error(f"异步处理财务操作通知失败: {e} 如果需要查看删除前的数据，请检查以前的邮件。")

        # 创建并启动后台线程
        thread = threading.Thread(target=send_notification)
        thread.daemon = True  # 设置为守护线程
        thread.start()

    def _get_operation_type(self, method, path):
        """根据HTTP方法和路径判断操作类型"""
        if method == 'POST':
            return 'CREATE'
        elif method in ['PUT', 'PATCH']:
            return 'UPDATE'
        elif method == 'DELETE':
            return 'DELETE'
        else:
            return 'UNKNOWN'
