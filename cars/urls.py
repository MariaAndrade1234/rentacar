from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CarBrandViewSet, CarModelViewSet, CarViewSet,
    CarDocumentViewSet, CarImageViewSet
)

router = DefaultRouter()
router.register(r'brands', CarBrandViewSet, basename='car-brand')
router.register(r'models', CarModelViewSet, basename='car-model')
router.register(r'documents', CarDocumentViewSet, basename='car-document')
router.register(r'images', CarImageViewSet, basename='car-image')
router.register(r'', CarViewSet, basename='car')

urlpatterns = [
    path('', include(router.urls)),
]
