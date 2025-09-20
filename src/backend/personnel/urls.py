from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PersonnelViewSet, ProjectGroupViewSet

router = DefaultRouter()
router.register(r'personnel', PersonnelViewSet)
router.register(r'project-groups', ProjectGroupViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
