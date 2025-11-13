from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import EvaluationRecordViewSet

router = DefaultRouter()
router.register(r'evaluation-records', EvaluationRecordViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]

