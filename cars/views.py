import logging
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import CarBrand, CarModel, Car, CarDocument, CarImage
from .serializers import (
    CarBrandSerializer, CarModelSerializer, CarListSerializer, 
    CarDetailSerializer, CarCreateUpdateSerializer,
    CarDocumentSerializer, CarImageSerializer
)

logger = logging.getLogger(__name__)


class CarBrandViewSet(viewsets.ModelViewSet):
    queryset = CarBrand.objects.all()
    serializer_class = CarBrandSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'country']
    ordering_fields = ['name']
    ordering = ['name']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]


class CarModelViewSet(viewsets.ModelViewSet):
    queryset = CarModel.objects.select_related('brand').all()
    serializer_class = CarModelSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['brand', 'year']
    search_fields = ['name', 'brand__name']
    ordering_fields = ['year', 'name']
    ordering = ['-year', 'name']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]


class CarViewSet(viewsets.ModelViewSet):
    # Optimized with select_related and prefetch_related
    queryset = Car.objects.select_related(
        'model',
        'model__brand'
    ).prefetch_related(
        'images',
        'documents'
    ).all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'is_available', 'model__brand', 'model', 'color', 'fuel_type', 'transmission']
    search_fields = ['license_plate', 'vin', 'model__name', 'model__brand__name']
    ordering_fields = ['daily_price', 'mileage']
    ordering = ['model__brand__name', 'model__name']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]
    
    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def list(self, request, *args, **kwargs):
        """List all cars with caching for public endpoint."""
        logger.debug("Listing cars (cached)")
        return super().list(request, *args, **kwargs)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CarListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CarCreateUpdateSerializer
        return CarDetailSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'available']:
            return [AllowAny()]
        return [IsAdminUser()]
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        available_cars = self.queryset.filter(is_available=True, status='AVAILABLE')
        serializer = self.get_serializer(available_cars, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_rented(self, request, pk=None):
        car = self.get_object()
        car.mark_as_rented()
        return Response({'status': 'Car marked as rented'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def mark_available(self, request, pk=None):
        car = self.get_object()
        car.mark_as_available()
        return Response({'status': 'Car marked as available'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def mark_maintenance(self, request, pk=None):
        car = self.get_object()
        car.mark_for_maintenance()
        return Response({'status': 'Car marked for maintenance'}, status=status.HTTP_200_OK)


class CarDocumentViewSet(viewsets.ModelViewSet):
    queryset = CarDocument.objects.select_related('car').all()
    serializer_class = CarDocumentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['car', 'document_type']
    ordering_fields = ['expiry_date']
    ordering = ['-expiry_date']
    permission_classes = [IsAdminUser]


class CarImageViewSet(viewsets.ModelViewSet):
    queryset = CarImage.objects.select_related('car').all()
    serializer_class = CarImageSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['car', 'is_primary']
    permission_classes = [IsAdminUser]
