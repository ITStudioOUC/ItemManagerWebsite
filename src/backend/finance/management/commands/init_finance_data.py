from django.core.management.base import BaseCommand
from finance.models import Department, Category

# 创建：python manage.py init_finance_data

class Command(BaseCommand):
    help = '初始化财务系统的部门和类别数据'

    def handle(self, *args, **options):
        # 创建部门
        departments = [
            '爱特工作室本部',
            '程序部',
            'Web部',
            '游戏部',
            'IOS部',
            'APP部',
            'UI部',
            '智能应用部',
            'OpenHarmony部',
            'FOSS部'
        ]

        for dept_name in departments:
            dept, created = Department.objects.get_or_create(name=dept_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'创建部门: {dept_name}'))
            else:
                self.stdout.write(f'部门已存在: {dept_name}')

        # 创建类别
        categories = [
            '办公用品',
            '设备采购',
            '软件授权',
            '差旅费',
            '会议费',
            '宣传费用',
            '日用品费用',
            '维护费用',
            '其他支出',
            '项目收入',
            '服务收入',
            '资金交接',
            '其他收入'
        ]

        for cat_name in categories:
            cat, created = Category.objects.get_or_create(name=cat_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'创建类别: {cat_name}'))
            else:
                self.stdout.write(f'类别已存在: {cat_name}')

        self.stdout.write(self.style.SUCCESS('初始化完成！'))
