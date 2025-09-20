from django.core.management.base import BaseCommand
from django.utils import timezone
from personnel.models import Personnel


class Command(BaseCommand):
    help = '检查人员任职结束时间，自动设置已到期人员为已卸任状态'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='仅显示将要更新的人员，不实际执行更新',
        )

    def handle(self, *args, **options):
        today = timezone.now().date()
        dry_run = options['dry_run']

        # 查找任职结束时间已到期但仍在职的人员
        expired_personnel = Personnel.objects.filter(
            end_date__lte=today,
            is_active=True
        )

        if not expired_personnel.exists():
            self.stdout.write(
                self.style.SUCCESS('没有需要设置为已卸任状态的人员')
            )
            return

        self.stdout.write(
            self.style.WARNING(f'发现 {expired_personnel.count()} 名任职已到期的人员:')
        )

        updated_count = 0
        for person in expired_personnel:
            self.stdout.write(
                f'  - {person.name} (学号: {person.student_id}) '
                f'任职结束时间: {person.end_date} '
                f'部门: {person.department.name} '
                f'职位: {person.position}'
            )

            if not dry_run:
                person.is_active = False
                person.save()
                updated_count += 1

        if dry_run:
            self.stdout.write(
                self.style.WARNING('这是预览模式，未实际更新任何数据')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'成功将 {updated_count} 名人员设置为已卸任状态')
            )
