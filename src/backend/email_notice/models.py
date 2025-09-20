from django.core.validators import EmailValidator
from django.db import models


class NotificationEmail(models.Model):
    """通知邮箱模型"""
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        verbose_name='邮箱地址'
    )
    is_enabled = models.BooleanField(
        default=True,
        verbose_name='是否启用'
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='描述'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        verbose_name = '通知邮箱'
        verbose_name_plural = '通知邮箱'
        ordering = ['-created_at']

    def __str__(self):
        status = "启用" if self.is_enabled else "禁用"
        return f"{self.email} ({status})"

class NotificationSettings(models.Model):
    """通知设置模型"""
    email_notification_enabled = models.BooleanField(
        default=True,
        verbose_name='邮件通知总开关'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        verbose_name = '通知设置'
        verbose_name_plural = '通知设置'

    def __str__(self):
        status = "开启" if self.email_notification_enabled else "关闭"
        return f"邮件通知: {status}"

    @classmethod
    def get_settings(cls):
        """获取通知设置（单例模式）"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
