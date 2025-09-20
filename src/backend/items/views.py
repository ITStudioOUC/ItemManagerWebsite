from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Item, ItemUsage, Category
from .serializers import (
    ItemSerializer, ItemDetailSerializer, ItemUsageSerializer,
    CategorySerializer, UserSerializer
)


class ItemViewSet(viewsets.ModelViewSet):
    """物品管理API"""
    authentication_classes = [JWTAuthentication]
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ItemDetailSerializer
        return ItemSerializer

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

        # 更新物品状态
        item.status = 'in_use'
        item.save()

        return Response(ItemUsageSerializer(usage).data)

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

        # 更新物品状态
        item.status = 'available'
        item.save()

        return Response(ItemUsageSerializer(current_usage).data)

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
    queryset = ItemUsage.objects.all()
    serializer_class = ItemUsageSerializer

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
