from django.test import TestCase
from django.core import mail
from .models import NotificationEmail, NotificationSettings
from .services import EmailNotificationService

class EmailNotificationTestCase(TestCase):
    def setUp(self):
        """设置测试数据"""
        self.email1 = NotificationEmail.objects.create(
            email="test1@example.com",
            is_enabled=True,
            description="测试邮箱1"
        )
        self.email2 = NotificationEmail.objects.create(
            email="test2@example.com",
            is_enabled=False,
            description="测试邮箱2"
        )

    def test_get_notification_settings(self):
        """测试获取通知设置"""
        settings = EmailNotificationService.get_notification_settings()
        self.assertTrue(settings['email_enabled'])
        self.assertIn("test1@example.com", settings['notification_emails'])
        self.assertNotIn("test2@example.com", settings['notification_emails'])

    def test_toggle_email_status(self):
        """测试切换邮箱状态"""
        result = EmailNotificationService.toggle_email_status(self.email2.id, True)
        self.assertTrue(result)

        self.email2.refresh_from_db()
        self.assertTrue(self.email2.is_enabled)

    def test_update_notification_emails(self):
        """测试更新通知邮箱"""
        emails_data = [
            {'email': 'new1@example.com', 'is_enabled': True, 'description': '新邮箱1'},
            {'email': 'new2@example.com', 'is_enabled': False, 'description': '新邮箱2'}
        ]

        result = EmailNotificationService.update_notification_emails(emails_data)
        self.assertTrue(result)

        # 检查数据库中的邮箱数量
        self.assertEqual(NotificationEmail.objects.count(), 2)
        self.assertTrue(NotificationEmail.objects.filter(email='new1@example.com').exists())
