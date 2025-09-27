from django.db import models
from django.contrib.auth.models import User


class Memo(models.Model):
    title = models.CharField(max_length=200, verbose_name="标题")
    content = models.TextField(verbose_name="内容", blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="创建者")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")

    class Meta:
        verbose_name = "备忘录"
        verbose_name_plural = "备忘录"
        ordering = ['-updated_at']

    def __str__(self):
        return self.title

    @property
    def content_preview(self):
        """返回内容的缩略预览"""
        if len(self.content) > 100:
            return self.content[:100] + "..."
        return self.content


class MemoImage(models.Model):
    memo = models.ForeignKey(Memo, on_delete=models.CASCADE, related_name='images', verbose_name="备忘录")
    image = models.ImageField(upload_to='memo_images/', verbose_name="图片")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="上传时间")
    alt_text = models.CharField(max_length=200, blank=True, verbose_name="图片描述")

    class Meta:
        verbose_name = "备忘录图片"
        verbose_name_plural = "备忘录图片"

    def __str__(self):
        return f"{self.memo.title} - 图片"
