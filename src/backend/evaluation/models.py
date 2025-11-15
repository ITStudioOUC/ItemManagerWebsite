from django.db import models
from django.utils import timezone


class EvaluationRecord(models.Model):
    """考评记录"""
    department = models.ForeignKey(
        'finance.Department',
        on_delete=models.CASCADE,
        related_name='evaluation_records',
        verbose_name='所属部门'
    )
    personnel = models.CharField(max_length=100, verbose_name='人员')
    grade = models.CharField(max_length=50, blank=True, verbose_name='年级')
    item_description = models.CharField(max_length=255, verbose_name='加/扣分事项说明')
    bonus_score = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='加分数值')
    deduction_score = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='扣分数值')
    remarks = models.CharField(max_length=255, blank=True, verbose_name='备注')
    total_score = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='总计分数')
    evaluation_date = models.DateField(default=timezone.now, verbose_name='考评日期')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '考评记录'
        verbose_name_plural = verbose_name
        ordering = ['-evaluation_date', '-created_at']
        indexes = [
            models.Index(fields=['department', 'evaluation_date']),
            models.Index(fields=['personnel', 'evaluation_date']),
            models.Index(fields=['evaluation_date']),
        ]

    def __str__(self):
        return f'{self.evaluation_date} {self.personnel} ({self.total_score})'

    def save(self, *args, **kwargs):
        self.total_score = (self.bonus_score or 0) - (self.deduction_score or 0)
        super().save(*args, **kwargs)
