from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Rental, RentalPayment, RentalReview, RentalDocument
from cars.serializers import CarListSerializer


class RentalListSerializer(serializers.ModelSerializer):
    """Serializer for Rental list view."""
    user_name = serializers.CharField(source='user.username', read_only=True)
    car_details = CarListSerializer(source='car', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Rental
        fields = [
            'id', 'user_name', 'car_details', 'start_date', 'end_date',
            'status', 'total_amount', 'is_overdue', 'created_at'
        ]


class RentalDetailSerializer(serializers.ModelSerializer):
    """Serializer for Rental detail view."""
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    car_details = CarListSerializer(source='car', read_only=True)
    duration_days = serializers.IntegerField(source='get_duration_days', read_only=True)
    actual_duration_days = serializers.IntegerField(source='get_actual_duration_days', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Rental
        fields = [
            'id', 'user', 'user_name', 'user_email', 'car', 'car_details',
            'start_date', 'end_date', 'actual_return_date', 'pickup_location',
            'dropoff_location', 'status', 'daily_rate', 'total_days', 'subtotal',
            'discount', 'tax', 'total_amount', 'mileage_start', 'mileage_end',
            'notes', 'cancellation_reason', 'duration_days', 'actual_duration_days',
            'is_overdue', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class RentalCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new Rental."""
    
    class Meta:
        model = Rental
        fields = [
            'user', 'car', 'start_date', 'end_date', 'pickup_location',
            'dropoff_location', 'daily_rate', 'discount', 'tax', 'notes'
        ]
    
    def validate(self, data):
        """Validate rental dates and car availability."""
        if data['start_date'] >= data['end_date']:
            raise serializers.ValidationError("End date must be after start date.")
        
        if data['start_date'] < timezone.now():
            raise serializers.ValidationError("Start date cannot be in the past.")
        
        if not data['car'].is_available:
            raise serializers.ValidationError("This car is not available for rental.")
        
        overlapping = Rental.objects.filter(
            car=data['car'],
            status__in=['CONFIRMED', 'ACTIVE']
        ).filter(
            start_date__lt=data['end_date'],
            end_date__gt=data['start_date']
        ).exists()
        
        if overlapping:
            raise serializers.ValidationError("This car is already booked for the selected dates.")
        
        return data
    
    def create(self, validated_data):
        """Create rental and calculate totals."""
        rental = Rental(**validated_data)
        rental.calculate_total_amount()
        rental.save()
        return rental


class RentalPaymentSerializer(serializers.ModelSerializer):
    """Serializer for RentalPayment."""
    rental_id = serializers.IntegerField(source='rental.id', read_only=True)
    
    class Meta:
        model = RentalPayment
        fields = [
            'id', 'rental', 'rental_id', 'amount', 'payment_method',
            'status', 'transaction_id', 'payment_date', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['payment_date', 'created_at', 'updated_at']


class RentalReviewSerializer(serializers.ModelSerializer):
    """Serializer for RentalReview."""
    user_name = serializers.CharField(source='rental.user.username', read_only=True)
    car_info = serializers.SerializerMethodField()
    
    class Meta:
        model = RentalReview
        fields = [
            'id', 'rental', 'user_name', 'car_info', 'rating',
            'comment', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_car_info(self, obj):
        return f"{obj.rental.car.model.brand.name} {obj.rental.car.model.name}"
    
    def validate_rating(self, value):
        """Validate rating is between 1 and 5."""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class RentalDocumentSerializer(serializers.ModelSerializer):
    """Serializer for RentalDocument."""
    
    class Meta:
        model = RentalDocument
        fields = [
            'id', 'rental', 'document_type', 'file_url',
            'description', 'uploaded_at'
        ]
        read_only_fields = ['uploaded_at']
