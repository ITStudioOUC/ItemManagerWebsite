from rest_framework import serializers
from .models import Memo, MemoImage


class MemoImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemoImage
        fields = ['id', 'image', 'uploaded_at', 'alt_text']


class MemoSerializer(serializers.ModelSerializer):
    images = MemoImageSerializer(many=True, read_only=True)
    content_preview = serializers.ReadOnlyField()
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Memo
        fields = ['id', 'title', 'content', 'content_preview', 'created_by', 'created_by_name',
                 'created_at', 'updated_at', 'is_active', 'images']
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class MemoListSerializer(serializers.ModelSerializer):
    content_preview = serializers.ReadOnlyField()
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Memo
        fields = ['id', 'title', 'content_preview', 'created_by_name', 'updated_at']