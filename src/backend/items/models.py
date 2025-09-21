from django.db import models
import os
import uuid


def get_item_image_path(instance, filename):
    """生成物品图片的存储路径"""
    # 如果物品还没有ID，先生成一个临时文件夹名
    item_id = instance.item.id if instance.item.id else str(uuid.uuid4())
    return f'items/{item_id}/initial/{filename}'


def get_usage_borrow_image_path(instance, filename):
    """生成借用时图片的存储路径"""
    item_id = instance.usage.item.id if instance.usage.item.id else str(uuid.uuid4())
    usage_id = instance.usage.id if instance.usage.id else str(uuid.uuid4())
    return f'items/{item_id}/usage/{usage_id}/borrow/{filename}'


def get_usage_return_image_path(instance, filename):
    """生成归还时图片的存储路径"""
    item_id = instance.usage.item.id if instance.usage.item.id else str(uuid.uuid4())
    usage_id = instance.usage.id if instance.usage.id else str(uuid.uuid4())
    return f'items/{item_id}/usage/{usage_id}/return/{filename}'


class Item(models.Model):
    """物品模型"""
    STATUS_CHOICES = [
        ('available', '可用'),
        ('in_use', '使用中'),
        ('maintenance', '维护中'),
        ('damaged', '损坏'),
        ('lost', '丢失'),
        ('abandoned', '已弃用'),
        ('prohibited', '禁止借用'),
    ]

    name = models.CharField(max_length=100, verbose_name='物品名称')
    description = models.TextField(blank=True, verbose_name='物品描述')
    serial_number = models.CharField(max_length=50, unique=True, verbose_name='序列号')
    category = models.CharField(max_length=50, verbose_name='物品类别')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name='物品状态')
    location = models.CharField(max_length=100, blank=True, verbose_name='存放位置')
    owner = models.CharField(max_length=100, blank=True, null=True, verbose_name='所有者')
    purchase_date = models.DateField(null=True, blank=True, verbose_name='购买日期')
    value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='价值')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '物品'
        verbose_name_plural = '物品'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.serial_number})"


class ItemImage(models.Model):
    """物品图片模型"""
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='images', verbose_name='物品')
    image = models.ImageField(upload_to=get_item_image_path, verbose_name='图片')
    description = models.CharField(max_length=200, blank=True, verbose_name='图片描述')
    is_primary = models.BooleanField(default=False, verbose_name='是否为主图')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')

    class Meta:
        verbose_name = '物品图片'
        verbose_name_plural = '物品图片'
        ordering = ['-is_primary', '-created_at']

    def __str__(self):
        return f"{self.item.name} - 图片"


class ItemUsage(models.Model):
    """物品使用记录模型"""
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name='物品')
    user = models.CharField(max_length=100, verbose_name='借用人姓名')
    borrower_contact = models.CharField(max_length=100, default="NONE", verbose_name='借用人联系方式')
    expected_return_time = models.DateTimeField(verbose_name='预计归还时间', blank=True, null=True)
    start_time = models.DateTimeField(verbose_name='开始使用时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束使用时间')
    purpose = models.CharField(max_length=200, verbose_name='使用目的')
    notes = models.TextField(blank=True, verbose_name='使用备注')
    is_returned = models.BooleanField(default=False, verbose_name='是否已归还')
    condition_before = models.CharField(max_length=200, blank=True, verbose_name='使用前状况')
    condition_after = models.CharField(max_length=200, blank=True, verbose_name='使用后状况')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='记录创建时间')

    class Meta:
        verbose_name = '使用记录'
        verbose_name_plural = '使用记录'
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.item.name} - {self.user} ({self.start_time.strftime('%Y-%m-%d %H:%M')})"


class UsageImage(models.Model):
    """使用记录图片模型"""
    IMAGE_TYPE_CHOICES = [
        ('borrow', '借用时'),
        ('return', '归还时'),
    ]

    usage = models.ForeignKey(ItemUsage, on_delete=models.CASCADE, related_name='images', verbose_name='使用记录')
    image = models.ImageField(upload_to='usage_images/', verbose_name='图片')
    image_type = models.CharField(max_length=10, choices=IMAGE_TYPE_CHOICES, verbose_name='图片类型')
    description = models.CharField(max_length=200, blank=True, verbose_name='图片描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # 保存后重新组织文件路径
        if self.image and self.usage_id and self.usage.item_id:
            import os
            import shutil
            from django.conf import settings

            old_path = self.image.path
            if self.image_type == 'borrow':
                new_relative_path = f'items/{self.usage.item_id}/usage/{self.usage_id}/borrow/{os.path.basename(old_path)}'
            else:
                new_relative_path = f'items/{self.usage.item_id}/usage/{self.usage_id}/return/{os.path.basename(old_path)}'

            new_path = os.path.join(settings.MEDIA_ROOT, new_relative_path)

            # 创建目录
            os.makedirs(os.path.dirname(new_path), exist_ok=True)

            # 移动文件
            if os.path.exists(old_path) and old_path != new_path:
                shutil.move(old_path, new_path)
                self.image.name = new_relative_path
                super().save(update_fields=['image'])

    class Meta:
        verbose_name = '使用记录图片'
        verbose_name_plural = '使用记录图片'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.usage.item.name} - {self.get_image_type_display()}"


class Category(models.Model):
    """物品类别模型"""
    name = models.CharField(max_length=50, unique=True, verbose_name='类别名称')
    description = models.TextField(blank=True, verbose_name='类别描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '物品类别'
        verbose_name_plural = '物品类别'
        ordering = ['name']

    def __str__(self):
        return self.name
