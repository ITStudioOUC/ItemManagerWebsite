from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Memo, MemoImage
from .serializers import MemoSerializer, MemoListSerializer, MemoImageSerializer


class MemoViewSet(viewsets.ModelViewSet):
    queryset = Memo.objects.filter(is_active=True)
    serializer_class = MemoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return MemoListSerializer
        return MemoSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        return queryset

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_image(self, request, pk=None):
        memo = self.get_object()
        image = request.FILES.get('image')
        alt_text = request.data.get('alt_text', '')

        if not image:
            return Response({'error': '请选择图片文件'}, status=status.HTTP_400_BAD_REQUEST)

        memo_image = MemoImage.objects.create(
            memo=memo,
            image=image,
            alt_text=alt_text
        )

        serializer = MemoImageSerializer(memo_image)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'])
    def delete_image(self, request, pk=None):
        memo = self.get_object()
        image_id = request.data.get('image_id')

        try:
            memo_image = MemoImage.objects.get(id=image_id, memo=memo)
            memo_image.delete()
            return Response({'message': '图片删除成功'}, status=status.HTTP_200_OK)
        except MemoImage.DoesNotExist:
            return Response({'error': '图片不存在'}, status=status.HTTP_404_NOT_FOUND)
