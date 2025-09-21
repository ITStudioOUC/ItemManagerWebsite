from django.core.management.base import BaseCommand
from items.models import Category

# 添加物品类别：python manage.py create_default_categories


class Command(BaseCommand):
    help = '创建默认的物品类别'

    def handle(self, *args, **options):
        # 默认物品类别列表
        default_categories = [
            {
                'name': '电子设备',
                'description': '包括电脑、手机、平板等电子产品'
            },
            {
                'name': '办公用品',
                'description': '办公桌椅、文具、打印机等办公设备'
            },
            {
                'name': '实验器材',
                'description': '实验室设备、仪器、工具等'
            },
            {
                'name': '家具',
                'description': '桌子、椅子、柜子等家具用品'
            },
            {
                'name': '图书资料',
                'description': '书籍、文档、资料等'
            },
            {
                'name': '工具设备',
                'description': '维修工具、测量仪器等'
            },
            {
                'name': '音响设备',
                'description': '音响、麦克风、投影仪等音视频设备'
            },
            {
                'name': '运动器材',
                'description': '体育用品、健身器材等'
            },
            {
                'name': '清洁用品',
                'description': '清洁工具、清洁剂等'
            },
            {
                'name': '网络设备',
                'description': '路由器、交换机、网线等网络相关设备'
            },
            {
                'name': '安全设备',
                'description': '监控摄像头、门禁系统、报警器等安全设备'
            },
            {
                'name': '医疗用品',
                'description': '急救包、体温计、血压计等医疗相关用品'
            },
            {
                'name': '厨房用具',
                'description': '微波炉、咖啡机、餐具等厨房设备'
            },
            {
                'name': '照明设备',
                'description': '台灯、吊灯、应急灯等照明用品'
            },
            {
                'name': '存储设备',
                'description': '硬盘、U盘、移动硬盘等存储设备'
            },
            {
                'name': '车辆工具',
                'description': '汽车配件、维修工具、车载设备等'
            },
            {
                'name': '服装用品',
                'description': '工作服、防护服、鞋帽等服装类物品'
            },
            {
                'name': '教学用品',
                'description': '黑板、白板、教学模型等教学设备'
            },
            {
                'name': '通讯设备',
                'description': '对讲机、电话、传真机等通讯设备'
            },
            {
                'name': '空调制冷',
                'description': '空调、风扇、加湿器等温度调节设备'
            },
            {
                'name': '消防设备',
                'description': '灭火器、烟雾报警器、消防栓等消防用品'
            },
            {
                'name': '软件许可',
                'description': '软件授权、许可证、数字资产等'
            },
            {
                'name': '包装材料',
                'description': '纸箱、胶带、包装袋等包装用品'
            },
            {
                'name': '园艺用品',
                'description': '花盆、园艺工具、肥料等园艺相关用品'
            },
            {
                'name': '其他',
                'description': '其他未分类的物品'
            }
        ]

        created_count = 0
        updated_count = 0

        for category_data in default_categories:
            category, created = Category.objects.get_or_create(
                name=category_data['name'],
                defaults={'description': category_data['description']}
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'创建类别: {category.name}')
                )
            else:
                # 更新描述（如果不同）
                if category.description != category_data['description']:
                    category.description = category_data['description']
                    category.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'更新类别: {category.name}')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n任务完成！创建了 {created_count} 个新类别，更新了 {updated_count} 个类别。'
            )
        )
