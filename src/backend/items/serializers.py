from django.contrib.auth.models import User
from rest_framework import serializers

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
            return {
                'username': current_usage.user,
                'contact': current_usage.borrower_contact
            }
        return None


class ItemUsageSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    item_serial = serializers.CharField(source='item.serial_number', read_only=True)

    class Meta:
        model = ItemUsage
        fields = [
            'id', 'item', 'item_name', 'item_serial', 'user', 'borrower_contact',
            'start_time', 'end_time', 'purpose', 'notes', 'is_returned',
            'condition_before', 'condition_after', 'expected_return_time', 'created_at'
        ]
        read_only_fields = ['created_at']


class ItemDetailSerializer(ItemSerializer):
    """物品详情序列化器，包含使用历史"""
    usage_history = serializers.SerializerMethodField()

    class Meta(ItemSerializer.Meta):
        fields = ItemSerializer.Meta.fields + ['usage_history']

    def get_usage_history(self, obj):
        """获取物品的使用历史"""
        usages = ItemUsage.objects.filter(item=obj).order_by('-start_time')[:10]
        return ItemUsageSerializer(usages, many=True).data
