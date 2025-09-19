from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FinancialRecordViewSet, DepartmentViewSet, CategoryViewSet, ProofImageViewSet

router = DefaultRouter()
router.register(r'finance', FinancialRecordViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'finance_categories', CategoryViewSet)
router.register(r'proof-images', ProofImageViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
