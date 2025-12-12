from django.urls import path
from .views import (
    CarBrandViewSet, CarModelViewSet, CarViewSet,
    CarDocumentViewSet, CarImageViewSet
)

urlpatterns = [
    path('brands/', CarBrandViewSet.as_view({'get': 'list', 'post': 'create'}), name='car-brand-list'),
    path('brands/<int:pk>/', CarBrandViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='car-brand-detail'),
    
    path('models/', CarModelViewSet.as_view({'get': 'list', 'post': 'create'}), name='car-model-list'),
    path('models/<int:pk>/', CarModelViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='car-model-detail'),
    
    path('documents/', CarDocumentViewSet.as_view({'get': 'list', 'post': 'create'}), name='car-document-list'),
    path('documents/<int:pk>/', CarDocumentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='car-document-detail'),
    
    path('images/', CarImageViewSet.as_view({'get': 'list', 'post': 'create'}), name='car-image-list'),
    path('images/<int:pk>/', CarImageViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='car-image-detail'),
    
    path('', CarViewSet.as_view({'get': 'list', 'post': 'create'}), name='car-list'),
    path('<int:pk>/', CarViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='car-detail'),
]
