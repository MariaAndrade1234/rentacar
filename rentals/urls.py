from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RentalViewSet, RentalPaymentViewSet,
    RentalReviewViewSet, RentalDocumentViewSet
)

router = DefaultRouter()
router.register(r'payments', RentalPaymentViewSet, basename='rental-payment')
router.register(r'reviews', RentalReviewViewSet, basename='rental-review')
router.register(r'documents', RentalDocumentViewSet, basename='rental-document')
router.register(r'', RentalViewSet, basename='rental')

urlpatterns = [
    path('', include(router.urls)),
]
