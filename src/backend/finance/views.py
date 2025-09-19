import os
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import FinancialRecord, Department, Category, ProofImage
from .serializers import (
    FinancialRecordWriteSerializer,
    FinancialRecordReadSerializer,
    DepartmentSerializer,
    CategorySerializer,
    ProofImageSerializer
)

class FinancialRecordViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows financial records to be viewed or edited.
    """
    queryset = FinancialRecord.objects.all()

    def get_serializer_class(self):
        """根据操作类型返回不同的序列化器"""
        if self.action in ['list', 'retrieve']:
            return FinancialRecordReadSerializer
        return FinancialRecordWriteSerializer

    @action(detail=True, methods=['post'])
    def upload_images(self, request, pk=None):
        """为财务记录上传多张凭证图片"""
        record = self.get_object()
        files = request.FILES.getlist('images')

        if not files:
            return Response({'error': '没有接收到图片文件'}, status=status.HTTP_400_BAD_REQUEST)

        created_images = []
        for file in files:
            proof_image = ProofImage.objects.create(
                financial_record=record,
                image=file,
                description=request.data.get('description', '')
            )
            created_images.append(ProofImageSerializer(proof_image).data)

        return Response({
            'message': f'成功上传 {len(created_images)} 张图片',
            'images': created_images
        }, status=status.HTTP_201_CREATED)


class ProofImageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows proof images to be viewed or edited.
    """
    queryset = ProofImage.objects.all()
    serializer_class = ProofImageSerializer

    def destroy(self, request, *args, **kwargs):
        """重写删除方法，确保删除图片记录时同时删除物理文件"""
        instance = self.get_object()

        # 获取文件路径
        file_path = None
        if instance.image:
            try:
                file_path = instance.image.path
            except (ValueError, AttributeError):
                # 如果文件路径无效或文件不存在，只删除数据库记录
                pass

        # 删除数据库记录
        super().destroy(request, *args, **kwargs)

        # 删除物理文件
        if file_path and os.path.isfile(file_path):
            try:
                os.remove(file_path)
                print(f"成功删除文件: {file_path}")
            except OSError as e:
                print(f"删除文件失败: {file_path}, 错误: {e}")
                # 即使文件删除失败，也不抛出异常，因为数据库记录已经删除

        return Response({'message': '图片删除成功'}, status=status.HTTP_200_OK)


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows departments to be viewed or edited.
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows categories to be viewed or edited.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
