from django.core.management.base import BaseCommand
from finance.models import Department
from personnel.models import ProjectGroup


class Command(BaseCommand):
    help = '创建示例的项目组数据'

    def handle(self, *args, **options):
        # 确保部门存在，如果不存在则创建
        departments_data = [
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

        self.stdout.write('正在创建部门...')
        for dept_name in departments_data:
            dept, created = Department.objects.get_or_create(name=dept_name)
            if created:
                self.stdout.write(f'  创建部门: {dept_name}')
            else:
                self.stdout.write(f'  部门已存在: {dept_name}')

        # 创建项目组数据
        project_groups_data = [
            # 程序部项目组
            {'name': '后端开发组', 'department_name': '程序部', 'description': '负责后端系统开发与维护'},
            {'name': '算法研究组', 'department_name': '程序部', 'description': '专注算法研究与优化'},

            # Web部项目组
            {'name': '前端开发组', 'department_name': 'Web部', 'description': '负责前端页面开发'},
            {'name': 'UI设计组', 'department_name': 'Web部', 'description': '负责用户界面设计'},

            # 游戏部项目组
            {'name': 'Unity开发组', 'department_name': '游戏部', 'description': '使用Unity引擎开发游戏'},
            {'name': '游戏策划组', 'department_name': '游戏部', 'description': '负责游戏策划与设计'},

            # IOS部项目组
            {'name': 'iOS原生开发组', 'department_name': 'IOS部', 'description': '开发iOS原生应用'},
            {'name': 'Swift开发组', 'department_name': 'IOS部', 'description': '使用Swift语言开发'},

            # APP部项目组
            {'name': 'Android开发组', 'department_name': 'APP部', 'description': '开发Android应用'},
            {'name': '跨平台开发组', 'department_name': 'APP部', 'description': '使用Flutter、React Native等开发'},

            # UI部项目组
            {'name': '视觉设计组', 'department_name': 'UI部', 'description': '负责视觉设计与品牌设计'},
            {'name': '交互设计组', 'department_name': 'UI部', 'description': '负责用户体验与交互设计'},

            # 智能应用部项目组
            {'name': 'AI研发组', 'department_name': '智能应用部', 'description': '人工智能技术研发'},
            {'name': '机器学习组', 'department_name': '智能应用部', 'description': '机器学习算法应用'},

            # OpenHarmony部项目组
            {'name': 'HarmonyOS开发组', 'department_name': 'OpenHarmony部', 'description': '开发HarmonyOS应用'},
            {'name': '鸿蒙系统组', 'department_name': 'OpenHarmony部', 'description': '鸿蒙生态系统开发'},

            # FOSS部项目组
            {'name': '开源项目组', 'department_name': 'FOSS部', 'description': '维护和开发开源项目'},
            {'name': 'Linux系统组', 'department_name': 'FOSS部', 'description': 'Linux系统维护与开发'},
        ]

        self.stdout.write('正在创建项目组...')
        for group_data in project_groups_data:
            try:
                department = Department.objects.get(name=group_data['department_name'])
                group, created = ProjectGroup.objects.get_or_create(
                    name=group_data['name'],
                    department=department,
                    defaults={'description': group_data['description']}
                )
                if created:
                    self.stdout.write(f'  创建项目组: {group_data["name"]} ({group_data["department_name"]})')
                else:
                    self.stdout.write(f'  项目组已存在: {group_data["name"]}')
            except Department.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'  部门不存在: {group_data["department_name"]}'))

        self.stdout.write(self.style.SUCCESS('示例数据创建完成！'))
        self.stdout.write('现在您可以在人员管理界面中看到这些项目组选项了。')
