from rest_framework import serializers
from .models import FinancialRecord, Department, Category, ProofImage


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProofImageSerializer(serializers.ModelSerializer):
    """凭证图片序列化器"""
    class Meta:
        model = ProofImage
        fields = ['id', 'image', 'description', 'uploaded_at']


class FinancialRecordWriteSerializer(serializers.ModelSerializer):
    """用于创建和更新财务记录的序列化器"""
    class Meta:
        model = FinancialRecord
        fields = '__all__'


class FinancialRecordReadSerializer(serializers.ModelSerializer):
    """用于读取财务记录的序列化器"""
    department = DepartmentSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    proof_images = ProofImageSerializer(many=True, read_only=True)

    class Meta:
        model = FinancialRecord
        fields = '__all__'


# 保持向后兼容的默认序列化器
class FinancialRecordSerializer(serializers.ModelSerializer):
    proof_images = ProofImageSerializer(many=True, read_only=True)

    class Meta:
        model = FinancialRecord
        fields = '__all__'
