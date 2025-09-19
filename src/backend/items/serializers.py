from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Item, ItemUsage, Category


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']


class ItemSerializer(serializers.ModelSerializer):
    current_user = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = [
            'id', 'name', 'description', 'serial_number', 'category', 'status',
            'location', 'owner', 'purchase_date', 'value', 'created_at', 'updated_at',
            'current_user'
        ]

    def get_current_user(self, obj):
        """获取当前正在使用该物品的用户"""
        current_usage = ItemUsage.objects.filter(
            item=obj, is_returned=False
        ).first()
        if current_usage:
            return UserSerializer(current_usage.user).data
        return None


class ItemUsageSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    item = ItemSerializer(read_only=True)
    item_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ItemUsage
        fields = [
            'id', 'item', 'item_id', 'user', 'user_id', 'start_time', 'end_time',
            'purpose', 'notes', 'is_returned', 'condition_before', 'condition_after',
            'created_at'
        ]

    def create(self, validated_data):
        # 当创建新的使用记录时，更新物品状态为使用中
        item = Item.objects.get(id=validated_data['item_id'])
        item.status = 'in_use'
        item.save()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # 当归还物品时，更新物品状态为可用
        if validated_data.get('is_returned', False) and not instance.is_returned:
            item = instance.item
            item.status = 'available'
            item.save()
        return super().update(instance, validated_data)


class ItemDetailSerializer(ItemSerializer):
    """物品详情序列化器，包含使用历史"""
    usage_history = serializers.SerializerMethodField()

    class Meta(ItemSerializer.Meta):
        fields = ItemSerializer.Meta.fields + ['usage_history']

    def get_usage_history(self, obj):
        """获取物品的使用历史"""
        usages = ItemUsage.objects.filter(item=obj).order_by('-start_time')[:10]
        return ItemUsageSerializer(usages, many=True).data
