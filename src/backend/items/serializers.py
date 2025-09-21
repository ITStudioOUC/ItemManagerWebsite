from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Item, ItemUsage, Category, ItemImage, UsageImage


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']


class ItemImageSerializer(serializers.ModelSerializer):
    """物品图片序列化器"""
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ItemImage
        fields = ['id', 'image', 'image_url', 'description', 'is_primary', 'created_at']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class UsageImageSerializer(serializers.ModelSerializer):
    """使用记录图片序列化器"""
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = UsageImage
        fields = ['id', 'image', 'image_url', 'image_type', 'description', 'created_at']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class ItemSerializer(serializers.ModelSerializer):
    current_user = serializers.SerializerMethodField()
    images = ItemImageSerializer(many=True, read_only=True)
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = [
            'id', 'name', 'description', 'serial_number', 'category', 'status',
            'location', 'owner', 'purchase_date', 'value', 'created_at', 'updated_at',
            'current_user', 'images', 'primary_image'
        ]

    def get_current_user(self, obj):
        """获取当前正在使用该物品的用户"""
        current_usage = ItemUsage.objects.filter(
            item=obj, is_returned=False
        ).first()
        if current_usage:
            return {
                'username': current_usage.user,
                'contact': current_usage.borrower_contact
            }
        return None

    def get_primary_image(self, obj):
        """获取主图片"""
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary_image.image.url)
        return None


class ItemUsageSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    item_serial = serializers.CharField(source='item.serial_number', read_only=True)
    images = UsageImageSerializer(many=True, read_only=True)
    borrow_images = serializers.SerializerMethodField()
    return_images = serializers.SerializerMethodField()

    class Meta:
        model = ItemUsage
        fields = [
            'id', 'item', 'item_name', 'item_serial', 'user', 'borrower_contact',
            'start_time', 'end_time', 'purpose', 'notes', 'is_returned',
            'condition_before', 'condition_after', 'expected_return_time', 'created_at',
            'images', 'borrow_images', 'return_images'
        ]
        read_only_fields = ['created_at']

    def get_borrow_images(self, obj):
        """获取借用时图片"""
        borrow_images = obj.images.filter(image_type='borrow')
        return UsageImageSerializer(borrow_images, many=True, context=self.context).data

    def get_return_images(self, obj):
        """获取归还时图片"""
        return_images = obj.images.filter(image_type='return')
        return UsageImageSerializer(return_images, many=True, context=self.context).data


class ItemDetailSerializer(ItemSerializer):
    """物品详情序列化器，包含使用历史"""
    usage_history = serializers.SerializerMethodField()

    class Meta(ItemSerializer.Meta):
        fields = ItemSerializer.Meta.fields + ['usage_history']

    def get_usage_history(self, obj):
        """获取物品的使用历史"""
        usages = ItemUsage.objects.filter(item=obj).order_by('-start_time')[:10]
        return ItemUsageSerializer(usages, many=True, context=self.context).data
