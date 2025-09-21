from django.contrib import admin

from .models import Item, ItemUsage, Category, ItemImage, UsageImage


class ItemImageInline(admin.TabularInline):
    """物品图片内联编辑"""
    model = ItemImage
    extra = 1
    fields = ['image', 'description', 'is_primary']


class UsageImageInline(admin.TabularInline):
    """使用记录图片内联编辑"""
    model = UsageImage
    extra = 1
    fields = ['image', 'image_type', 'description']


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'serial_number', 'category', 'status', 'location', 'owner', 'created_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['name', 'serial_number', 'description', 'owner']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ItemImageInline]
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description', 'serial_number', 'category')
        }),
        ('状态和位置', {
            'fields': ('status', 'location', 'owner')
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
    list_display = ['item', 'user', 'borrower_contact', 'start_time', 'end_time', 'is_returned', 'purpose']
    list_filter = ['is_returned', 'start_time', 'item__category']
    search_fields = ['item__name', 'user', 'purpose', 'borrower_contact']
    readonly_fields = ['created_at']
    inlines = [UsageImageInline]
    fieldsets = (
        ('使用信息', {
            'fields': ('item', 'user', 'borrower_contact', 'purpose', 'notes')
        }),
        ('时间信息', {
            'fields': ('start_time', 'end_time', 'expected_return_time', 'is_returned')
        }),
        ('状况记录', {
            'fields': ('condition_before', 'condition_after')
        }),
        ('系统信息', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )


@admin.register(ItemImage)
class ItemImageAdmin(admin.ModelAdmin):
    list_display = ['item', 'description', 'is_primary', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['item__name', 'description']
    readonly_fields = ['created_at']


@admin.register(UsageImage)
class UsageImageAdmin(admin.ModelAdmin):
    list_display = ['usage', 'image_type', 'description', 'created_at']
    list_filter = ['image_type', 'created_at']
    search_fields = ['usage__item__name', 'usage__user', 'description']
    readonly_fields = ['created_at']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
