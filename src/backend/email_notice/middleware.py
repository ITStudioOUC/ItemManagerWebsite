import json
import logging
import threading

from django.utils.deprecation import MiddlewareMixin

from .services import EmailNotificationService

logger = logging.getLogger(__name__)

class EmailNotificationMiddleware(MiddlewareMixin):
    """邮件通知中间件"""

    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)

    def process_response(self, request, response):
        """处理响应，在数据修改操作成功后异步发送邮件通知"""
        try:
            # 只处理API请求
            if not request.path.startswith('/api/'):
                return response

            # 排除凭证相关的API路径，这些已经在视图中单独处理
            if  '/proof-images/' in request.path :
                return response

            # 只处理数据新增修改操作，但排除DELETE操作，毕竟删除操作已经另外重写
            if request.method not in ['POST', 'PUT', 'PATCH']:
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
            elif '/api/personnel/' in request.path:
                self._handle_personnel_operation_async(request, response, user_info)
            elif '/api/departments/' in request.path:
                self._handle_department_operation_async(request, response, user_info)
            elif '/api/project-groups/' in request.path:
                self._handle_project_group_operation_async(request, response, user_info)

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
                    'item_name': item_data.get('item_name', ''),
                    'item_serial': item_data.get('item_serial', ''),
                    'serial_number': item_data.get('serial_number', ''),
                    'category': item_data.get('category', ''),
                    'status': item_data.get('status', ''),
                    'location': item_data.get('location', ''),
                    'description': item_data.get('description', ''),
                    'owner': item_data.get('owner', ''),
                    'purchase_date': item_data.get('purchase_date', ''),
                    'value': item_data.get('value', ''),
                    'user': item_data.get('user', ''),
                    'borrower_contact': item_data.get('borrower_contact', ''),
                    'start_time': item_data.get('start_time', ''),
                    'end_time': item_data.get('end_time', ''),
                    'purpose': item_data.get('purpose', ''),
                    'notes': item_data.get('notes', ''),
                    'is_returned': item_data.get('is_returned', ''),
                    'condition_before': item_data.get('condition_before', ''),
                    'condition_after': item_data.get('condition_after', ''),
                    'timestamp': item_data.get('updated_at', ''),
                    'operation_path': request.path,
                    'operation_method': request.method
                }

                EmailNotificationService.send_operation_notification(
                    operation_type, '物品', notification_data, user_info
                )

            except Exception as e:
                logger.error(f"异步处理物品操作通知失败: {e}")

        # 创建并启动后台线程
        thread = threading.Thread(target=send_notification)
        thread.daemon = True  # 设置为守护线程
        thread.start()

    def _handle_finance_operation_async(self, request, response, user_info):
        """异步处理财务操作"""
        def send_notification():
            try:
                operation_type = self._get_operation_type(request.method, request.path)

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
                    'timestamp': finance_data.get('updated_at', ''),
                    'operation_path': request.path,
                    'operation_method': request.method
                }

                EmailNotificationService.send_operation_notification(
                    operation_type, '财务记录', notification_data, user_info
                )

            except Exception as e:
                logger.error(f"异步处理财务操作通知失败: {e}")

        # 创建并启动后台线程
        thread = threading.Thread(target=send_notification)
        thread.daemon = True  # 设置为守护线程
        thread.start()

    def _handle_personnel_operation_async(self, request, response, user_info):
        """异步处理人员操作"""
        def send_notification():
            try:
                operation_type = self._get_operation_type(request.method, request.path)

                # 尝试从响应中获取数据
                if hasattr(response, 'data'):
                    personnel_data = response.data
                else:
                    try:
                        content = response.content.decode('utf-8')
                        personnel_data = json.loads(content) if content else {}
                    except:
                        personnel_data = {}

                # 确保personnel_data不为None
                if personnel_data is None:
                    personnel_data = {}

                # 构建通知数据，使用正确的字段名
                message = ''
                if 'message' in personnel_data:
                    message = personnel_data['message', '']
                if 'data' in personnel_data:
                    personnel_data = personnel_data['data', '']
                notification_data = {
                    'message': message,
                    'id': personnel_data.get('id', ''),
                    'name': personnel_data.get('name', ''),
                    'student_id': personnel_data.get('student_id', ''),
                    'gender': personnel_data.get('gender', ''),
                    'grader_major': personnel_data.get('grade_major', ''),
                    'department': personnel_data.get('department', ''),
                    'project_group': personnel_data.get('project_group', ''),
                    'project_group_name': personnel_data.get('project_group_name', ''),
                    'position': personnel_data.get('position', ''),
                    'start_date': personnel_data.get('start_date', ''),
                    'end_date': personnel_data.get('end_date', ''),
                    'is_active': personnel_data.get('is_active', ''),
                    'phone': personnel_data.get('phone', ''),
                    'qq': personnel_data.get('qq', ''),
                    'email': personnel_data.get('email', ''),
                    'description': personnel_data.get('description', ''),
                    'timestamp': personnel_data.get('updated_at', ''),
                    'operation_path': request.path,
                    'operation_method': request.method
                }

                EmailNotificationService.send_operation_notification(
                    operation_type, '人员', notification_data, user_info
                )

            except Exception as e:
                logger.error(f"异步处理人员操作通知失败: {e}")

        # 创建并启动后台线程
        thread = threading.Thread(target=send_notification)
        thread.daemon = True  # 设置为守护线程
        thread.start()

    def _handle_department_operation_async(self, request, response, user_info):
        """异步处理部门操作"""
        def send_notification():
            try:
                operation_type = self._get_operation_type(request.method, request.path)

                # 尝试从响应中获取数据
                if hasattr(response, 'data'):
                    department_data = response.data
                else:
                    try:
                        content = response.content.decode('utf-8')
                        department_data = json.loads(content) if content else {}
                    except:
                        department_data = {}

                # 确保department_data不为None
                if department_data is None:
                    department_data = {}

                # 构建通知数据
                notification_data = {
                    'id': department_data.get('id', ''),
                    'name': department_data.get('name', ''),
                    'timestamp': department_data.get('updated_at', ''),
                    'operation_path': request.path,
                    'operation_method': request.method
                }

                EmailNotificationService.send_operation_notification(
                    operation_type, '部门', notification_data, user_info
                )

            except Exception as e:
                logger.error(f"异步处理部门操作通知失败: {e}")

        # 创建并启动后台线程
        thread = threading.Thread(target=send_notification)
        thread.daemon = True  # 设置为守护线程
        thread.start()

    def _handle_project_group_operation_async(self, request, response, user_info):
        """异步处理项目组操作"""
        def send_notification():
            try:
                operation_type = self._get_operation_type(request.method, request.path)

                # 尝试从响应中获取数据
                if hasattr(response, 'data'):
                    project_group_data = response.data
                else:
                    try:
                        content = response.content.decode('utf-8')
                        project_group_data = json.loads(content) if content else {}
                    except:
                        project_group_data = {}

                # 确保project_group_data不为None
                if project_group_data is None:
                    project_group_data = {}

                # 构建通知数据
                notification_data = {
                    'id': project_group_data.get('id', ''),
                    'name': project_group_data.get('name', ''),
                    'department': project_group_data.get('department', ''),
                    'department_name': project_group_data.get('department_name', ''),
                    'description': project_group_data.get('description', ''),
                    'timestamp': project_group_data.get('updated_at', ''),
                    'operation_path': request.path,
                    'operation_method': request.method
                }

                EmailNotificationService.send_operation_notification(
                    operation_type, '项目组', notification_data, user_info
                )

            except Exception as e:
                logger.error(f"异步处理项目组操作通知失败: {e}")

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
        else:
            return 'UNKNOWN'
