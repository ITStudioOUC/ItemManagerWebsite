from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'items', views.ItemViewSet)
router.register(r'usages', views.ItemUsageViewSet)
router.register(r'item_categories', views.CategoryViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'item-images', views.ItemImageViewSet)
router.register(r'usage-images', views.UsageImageViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
