from django.contrib import admin
from .models import NotificationEmail, NotificationSettings

@admin.register(NotificationEmail)
class NotificationEmailAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_enabled', 'description', 'created_at')
    list_filter = ('is_enabled', 'created_at')
    search_fields = ('email', 'description')
    list_editable = ('is_enabled',)
    ordering = ('-created_at',)

@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ('email_notification_enabled', 'updated_at')

    def has_add_permission(self, request):
        # 只允许存在一个设置实例
        return not NotificationSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # 不允许删除设置
        return False
