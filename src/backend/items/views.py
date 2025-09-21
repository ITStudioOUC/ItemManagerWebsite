from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Item, ItemUsage, Category, ItemImage, UsageImage
from .serializers import (
    ItemSerializer, ItemDetailSerializer, ItemUsageSerializer,
    CategorySerializer, UserSerializer, ItemImageSerializer, UsageImageSerializer
)


class ItemViewSet(viewsets.ModelViewSet):
    """物品管理API"""
    authentication_classes = [JWTAuthentication]
    parser_classes = [MultiPartParser, FormParser]
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ItemDetailSerializer
        return ItemSerializer

    def create(self, request, *args, **kwargs):
        """创建物品，强制要求上传至少一张图片"""
        # 检查是否上传了图片
        images = request.FILES.getlist('images')
        if not images:
            return Response(
                {'error': '创建物品时必须上传至少一张图片'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 创建物品
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save()

        # 保存图片
        for i, image in enumerate(images):
            ItemImage.objects.create(
                item=item,
                image=image,
                description=request.data.get(f'image_descriptions[{i}]', ''),
                is_primary=(i == 0)  # 第一张图片设为主图
            )

        # 返回包含图片的完整数据
        response_serializer = ItemDetailSerializer(item, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def upload_images(self, request, pk=None):
        """上传物品图片"""
        item = self.get_object()
        images = request.FILES.getlist('images')

        if not images:
            return Response(
                {'error': '请选择要上传的图片'},
                status=status.HTTP_400_BAD_REQUEST
            )

        uploaded_images = []
        for i, image in enumerate(images):
            item_image = ItemImage.objects.create(
                item=item,
                image=image,
                description=request.data.get(f'image_descriptions[{i}]', ''),
                is_primary=False
            )
            uploaded_images.append(item_image)

        serializer = ItemImageSerializer(uploaded_images, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def set_primary_image(self, request, pk=None):
        """设置主图片"""
        item = self.get_object()
        image_id = request.data.get('image_id')

        try:
            # 取消当前主图
            item.images.filter(is_primary=True).update(is_primary=False)
            # 设置新主图
            new_primary = item.images.get(id=image_id)
            new_primary.is_primary = True
            new_primary.save()

            return Response({'message': '主图设置成功'})
        except ItemImage.DoesNotExist:
            return Response(
                {'error': '图片不存在'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def borrow(self, request, pk=None):
        """借用物品"""
        item = self.get_object()

        if item.status != 'available':
            return Response(
                {'error': '物品当前不可用'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_name = request.data.get('user_name')
        user_contact = request.data.get('user_contact', '')
        purpose = request.data.get('purpose', '')
        notes = request.data.get('notes', '')
        condition_before = request.data.get('condition_before', '')

        if not user_name:
            return Response(
                {'error': '请输入使用者姓名'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 创建使用记录
        usage = ItemUsage.objects.create(
            item=item,
            user=user_name,
            borrower_contact=user_contact,
            start_time=timezone.now(),
            purpose=purpose,
            notes=notes,
            condition_before=condition_before
        )

        # 保存借用时的图片
        borrow_images = request.FILES.getlist('borrow_images')
        for i, image in enumerate(borrow_images):
            UsageImage.objects.create(
                usage=usage,
                image=image,
                image_type='borrow',
                description=request.data.get(f'borrow_image_descriptions[{i}]', '')
            )

        # 更新物品状态
        item.status = 'in_use'
        item.save()

        response_serializer = ItemUsageSerializer(usage, context={'request': request})
        return Response(response_serializer.data)

    @action(detail=True, methods=['post'])
    def return_item(self, request, pk=None):
        """归还物品"""
        item = self.get_object()

        # 查找当前的使用记录
        current_usage = ItemUsage.objects.filter(
            item=item, is_returned=False
        ).first()

        if not current_usage:
            return Response(
                {'error': '该物品未被借用'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 更新使用记录
        current_usage.end_time = timezone.now()
        current_usage.is_returned = True
        current_usage.condition_after = request.data.get('condition_after', '')
        current_usage.notes = request.data.get('return_notes', current_usage.notes)
        current_usage.save()

        # 保存归还时的图片
        return_images = request.FILES.getlist('return_images')
        for i, image in enumerate(return_images):
            UsageImage.objects.create(
                usage=current_usage,
                image=image,
                image_type='return',
                description=request.data.get(f'return_image_descriptions[{i}]', '')
            )

        # 更新物品状态
        item.status = 'available'
        item.save()

        response_serializer = ItemUsageSerializer(current_usage, context={'request': request})
        return Response(response_serializer.data)

    @action(detail=False)
    def available(self, request):
        """获取可用物品列表"""
        items = self.queryset.filter(status='available')
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def in_use(self, request):
        """获取使用中的物品列表"""
        items = self.queryset.filter(status='in_use')
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)


class ItemUsageViewSet(viewsets.ModelViewSet):
    """使用记录管理API"""
    authentication_classes = [JWTAuthentication]
    parser_classes = [MultiPartParser, FormParser]
    queryset = ItemUsage.objects.all()
    serializer_class = ItemUsageSerializer

    @action(detail=True, methods=['post'])
    def upload_images(self, request, pk=None):
        """上传使用记录图片"""
        usage = self.get_object()
        images = request.FILES.getlist('images')
        image_type = request.data.get('image_type', 'borrow')

        if not images:
            return Response(
                {'error': '请选择要上传的图片'},
                status=status.HTTP_400_BAD_REQUEST
            )

        uploaded_images = []
        for i, image in enumerate(images):
            usage_image = UsageImage.objects.create(
                usage=usage,
                image=image,
                image_type=image_type,
                description=request.data.get(f'image_descriptions[{i}]', '')
            )
            uploaded_images.append(usage_image)

        serializer = UsageImageSerializer(uploaded_images, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False)
    def current(self, request):
        """获取当前使用中的记录"""
        usages = self.queryset.filter(is_returned=False)
        serializer = self.get_serializer(usages, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def by_user(self, request):
        """根据用户姓名获取使用记录"""
        user_name = request.query_params.get('user_name')
        if user_name:
            usages = self.queryset.filter(user__icontains=user_name)
            serializer = self.get_serializer(usages, many=True)
            return Response(serializer.data)
        return Response({'error': '请提供用户姓名'}, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(viewsets.ModelViewSet):
    """物品类别管理API"""
    authentication_classes = [JWTAuthentication]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """用户管理API（只读）"""
    authentication_classes = [JWTAuthentication]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ItemImageViewSet(viewsets.ModelViewSet):
    """物品图片管理API"""
    authentication_classes = [JWTAuthentication]
    parser_classes = [MultiPartParser, FormParser]
    queryset = ItemImage.objects.all()
    serializer_class = ItemImageSerializer


class UsageImageViewSet(viewsets.ModelViewSet):
    """使用记录图片管理API"""
    authentication_classes = [JWTAuthentication]
    parser_classes = [MultiPartParser, FormParser]
    queryset = UsageImage.objects.all()
    serializer_class = UsageImageSerializer
