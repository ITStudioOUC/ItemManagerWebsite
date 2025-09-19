from django.db import models
from django.contrib.auth.models import User


def proof_image_upload_path(instance, filename):
    """
    自定义文件上传路径
    格式: proofs/{记录ID}-{年月日}/{文件名}
    """
    record = instance.financial_record
    date_str = record.transaction_date.strftime('%Y%m%d')
    folder_name = f"{record.id}-{date_str}"
    return f'proofs/{folder_name}/{filename}'


class Department(models.Model):
    """部门"""
    name = models.CharField(max_length=100, unique=True, verbose_name="部门名称")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "部门"
        verbose_name_plural = verbose_name


class Category(models.Model):
    """财务记录类别"""
    name = models.CharField(max_length=100, unique=True, verbose_name="类别名称")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "财务类别"
        verbose_name_plural = verbose_name


class FinancialRecord(models.Model):
    """财务记录"""
    RECORD_TYPE_CHOICES = [
        ('expense', '支出'),
        ('income', '收入'),
    ]

    title = models.CharField(max_length=200, verbose_name="标题")
    description = models.TextField(blank=True, null=True, verbose_name="描述")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="金额")
    record_type = models.CharField(max_length=10, choices=RECORD_TYPE_CHOICES, verbose_name="记录类型")
    transaction_date = models.DateField(verbose_name="交易日期")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="所属部门")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="类别")
    fund_manager = models.CharField(max_length=100, blank=True, null=True, verbose_name="批准人")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="创建人")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return f"{self.title} - {self.amount}"

    class Meta:
        verbose_name = "财务记录"
        verbose_name_plural = verbose_name
        ordering = ['-transaction_date']


class ProofImage(models.Model):
    """凭证图片"""
    financial_record = models.ForeignKey(FinancialRecord, on_delete=models.CASCADE, related_name='proof_images', verbose_name="财务记录")
    image = models.ImageField(upload_to=proof_image_upload_path, verbose_name="凭证图片")
    description = models.CharField(max_length=200, blank=True, null=True, verbose_name="图片描述")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="上传时间")

    def __str__(self):
        return f"{self.financial_record.title} - 凭证{self.id}"

    class Meta:
        verbose_name = "凭证图片"
        verbose_name_plural = verbose_name
