import logging
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import Rental, RentalPayment, RentalReview, RentalDocument
from .serializers import (
    RentalListSerializer, RentalDetailSerializer, RentalCreateSerializer,
    RentalPaymentSerializer, RentalReviewSerializer, RentalDocumentSerializer
)

logger = logging.getLogger(__name__)


class RentalViewSet(viewsets.ModelViewSet):
    # Optimized queryset with select_related and prefetch_related
    queryset = Rental.objects.select_related(
        'user',
        'car',
        'car__model',
        'car__model__brand'
    ).prefetch_related(
        'payments',
        'documents',
        'review'
    ).all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'user', 'car']
    search_fields = ['user__username', 'car__license_plate', 'pickup_location', 'dropoff_location']
    ordering_fields = ['start_date', 'end_date', 'total_amount', 'created_at']
    ordering = ['-created_at']
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return RentalListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return RentalCreateSerializer
        return RentalDetailSerializer
    
    def get_queryset(self):
        """Get queryset with caching for non-admin users."""
        if self.request.user.is_staff:
            logger.debug("Admin user accessing all rentals")
            return self.queryset
        
        # Cache user's rentals for 5 minutes
        cache_key = f'user_rentals_{self.request.user.id}'
        cached_rentals = cache.get(cache_key)
        
        if cached_rentals is not None:
            logger.debug(f"Cache hit for user {self.request.user.id} rentals")
            return cached_rentals
        
        user_rentals = self.queryset.filter(user=self.request.user)
        cache.set(cache_key, user_rentals, 300)  # 5 minutes
        logger.debug(f"Cache miss for user {self.request.user.id} rentals")
        
        return user_rentals
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm a pending rental."""
        rental = self.get_object()
        if rental.status != 'PENDING':
            return Response(
                {'error': 'Only pending rentals can be confirmed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rental.status = 'CONFIRMED'
        rental.save()
        return Response({'status': 'Rental confirmed'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        rental = self.get_object()
        if rental.status != 'CONFIRMED':
            return Response(
                {'error': 'Only confirmed rentals can be started'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rental.status = 'ACTIVE'
        rental.mileage_start = request.data.get('mileage_start')
        rental.car.mark_as_rented()
        rental.save()
        return Response({'status': 'Rental started'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        rental = self.get_object()
        if rental.status != 'ACTIVE':
            return Response(
                {'error': 'Only active rentals can be completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rental.status = 'COMPLETED'
        rental.actual_return_date = timezone.now()
        rental.mileage_end = request.data.get('mileage_end')
        rental.car.mark_as_available()
        rental.save()
        return Response({'status': 'Rental completed'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a rental."""
        rental = self.get_object()
        if rental.status in ['COMPLETED', 'CANCELLED']:
            return Response(
                {'error': 'Cannot cancel completed or already cancelled rentals'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rental.status = 'CANCELLED'
        rental.cancellation_reason = request.data.get('reason', '')
        if rental.car.status == 'RENTED':
            rental.car.mark_as_available()
        rental.save()
        return Response({'status': 'Rental cancelled'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def my_rentals(self, request):
        rentals = self.queryset.filter(user=request.user)
        serializer = self.get_serializer(rentals, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        active_rentals = self.queryset.filter(status='ACTIVE')
        serializer = self.get_serializer(active_rentals, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        overdue_rentals = self.queryset.filter(
            status='ACTIVE',
            end_date__lt=timezone.now()
        )
        serializer = self.get_serializer(overdue_rentals, many=True)
        return Response(serializer.data)


class RentalPaymentViewSet(viewsets.ModelViewSet):
    queryset = RentalPayment.objects.select_related('rental').all()
    serializer_class = RentalPaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['rental', 'status', 'payment_method']
    ordering_fields = ['payment_date', 'amount']
    ordering = ['-payment_date']
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(rental__user=self.request.user)


class RentalReviewViewSet(viewsets.ModelViewSet):
    queryset = RentalReview.objects.select_related('rental__user', 'rental__car__model__brand').all()
    serializer_class = RentalReviewSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['rental', 'rating']
    ordering_fields = ['rating', 'created_at']
    ordering = ['-created_at']
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(rental__user=self.request.user)


class RentalDocumentViewSet(viewsets.ModelViewSet):
    queryset = RentalDocument.objects.select_related('rental').all()
    serializer_class = RentalDocumentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['rental', 'document_type']
    ordering_fields = ['uploaded_at']
    ordering = ['-uploaded_at']
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(rental__user=self.request.user)
