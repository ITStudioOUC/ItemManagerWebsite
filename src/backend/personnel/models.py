from django.db import models
from django.core.validators import RegexValidator
from finance.models import Department


class ProjectGroup(models.Model):
    """项目组模型"""
    name = models.CharField(max_length=100, unique=True, verbose_name="项目组名称")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="所属部门")
    description = models.TextField(blank=True, null=True, verbose_name="项目组描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "项目组"
        verbose_name_plural = verbose_name
        ordering = ['department', 'name']

    def __str__(self):
        return f"{self.department.name} - {self.name}"


class Personnel(models.Model):
    """人员信息模型"""
    GENDER_CHOICES = [
        ('male', '男'),
        ('female', '女'),
    ]

    # 基本信息
    name = models.CharField(max_length=50, verbose_name="姓名")
    student_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="学号",
        validators=[RegexValidator(
            regex=r'^\d{8,12}$',
            message='学号应为8-12位数字'
        )]
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name="性别")
    grade_major = models.CharField(max_length=100, verbose_name="年级专业")

    # 职位信息
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="所属部门")
    project_group = models.ForeignKey(
        ProjectGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="项目组"
    )
    position = models.CharField(max_length=50, verbose_name="职位")
    start_date = models.DateField(verbose_name="任职开始时间")
    end_date = models.DateField(null=True, blank=True, verbose_name="任职结束时间")
    is_active = models.BooleanField(default=True, verbose_name="是否在职")

    # 联系方式
    phone = models.CharField(
        max_length=11,
        verbose_name="手机号",
        validators=[RegexValidator(
            regex=r'^1[3-9]\d{9}$',
            message='请输入有效的手机号码'
        )]
    )
    qq = models.CharField(
        max_length=15,
        verbose_name="QQ号",
        validators=[RegexValidator(
            regex=r'^\d{5,15}$',
            message='QQ号应为5-15位数字'
        )]
    )
    email = models.EmailField(verbose_name="邮箱")

    # 详细信息
    description = models.TextField(blank=True, null=True, verbose_name="备注信息")

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "人员信息"
        verbose_name_plural = verbose_name
        ordering = ['-is_active', 'department', 'position', 'name']
        indexes = [
            models.Index(fields=['department', 'is_active']),
            models.Index(fields=['student_id']),
        ]

    def __str__(self):
        return f"{self.name} ({self.department.name} - {self.position})"

    @property
    def status_display(self):
        """返回在职状态显示"""
        if self.is_active:
            return "在职"
        return "已卸任"

    def save(self, *args, **kwargs):
        """保存时自动更新在职状态"""
        from django.utils import timezone

        # 如果设置了结束时间且已到期，自动设置为已卸任
        if self.end_date and self.end_date <= timezone.now().date():
            self.is_active = False

        super().save(*args, **kwargs)

    @classmethod
    def check_and_update_expired_personnel(cls):
        """检查并更新所有已到期的人员状态"""
        from django.utils import timezone
        today = timezone.now().date()

        expired_personnel = cls.objects.filter(
            end_date__lte=today,
            is_active=True
        )

        updated_count = expired_personnel.update(is_active=False)
        return updated_count, list(expired_personnel.values_list('name', flat=True))
