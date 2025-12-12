from django.urls import path
from .views import (
    RentalViewSet, RentalPaymentViewSet,
    RentalReviewViewSet, RentalDocumentViewSet
)

urlpatterns = [
    path('payments/', RentalPaymentViewSet.as_view({'get': 'list', 'post': 'create'}), name='rental-payment-list'),
    path('payments/<int:pk>/', RentalPaymentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='rental-payment-detail'),
    
    path('reviews/', RentalReviewViewSet.as_view({'get': 'list', 'post': 'create'}), name='rental-review-list'),
    path('reviews/<int:pk>/', RentalReviewViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='rental-review-detail'),
    
    path('documents/', RentalDocumentViewSet.as_view({'get': 'list', 'post': 'create'}), name='rental-document-list'),
    path('documents/<int:pk>/', RentalDocumentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='rental-document-detail'),
    
    path('', RentalViewSet.as_view({'get': 'list', 'post': 'create'}), name='rental-list'),
    path('<int:pk>/', RentalViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='rental-detail'),
]
