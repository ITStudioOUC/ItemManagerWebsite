from django.contrib import admin

from .models import Item, ItemUsage, Category


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'serial_number', 'category', 'status', 'location', 'created_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['name', 'serial_number', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description', 'serial_number', 'category')
        }),
        ('状态和位置', {
            'fields': ('status', 'location')
        }),
        ('购买信息', {
            'fields': ('purchase_date', 'value')
        }),
        ('系统信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(ItemUsage)
class ItemUsageAdmin(admin.ModelAdmin):
    list_display = ['item', 'user', 'start_time', 'end_time', 'is_returned', 'purpose']
    list_filter = ['is_returned', 'start_time', 'item__category']
    search_fields = ['item__name', 'user__username', 'purpose']
    readonly_fields = ['created_at']
    fieldsets = (
        ('使用信息', {
            'fields': ('item', 'user', 'purpose', 'notes')
        }),
        ('时间信息', {
            'fields': ('start_time', 'end_time', 'is_returned')
        }),
        ('状况记录', {
            'fields': ('condition_before', 'condition_after')
        }),
        ('系统信息', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
