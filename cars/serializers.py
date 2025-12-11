from rest_framework import serializers
from .models import CarBrand, CarModel, Car, CarDocument, CarImage


class CarBrandSerializer(serializers.ModelSerializer):
    total_models = serializers.SerializerMethodField()
    
    class Meta:
        model = CarBrand
        fields = ['id', 'name', 'country', 'description', 'logo_url', 'total_models', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_total_models(self, obj):
        return obj.models.count()


class CarModelSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    total_cars = serializers.SerializerMethodField()
    
    class Meta:
        model = CarModel
        fields = [
            'id', 'brand', 'brand_name', 'name', 'year', 'description',
            'total_cars', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_total_cars(self, obj):
        return obj.cars.count()


class CarImageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CarImage
        fields = ['id', 'image_url', 'description', 'is_primary', 'created_at']
        read_only_fields = ['created_at']


class CarDocumentSerializer(serializers.ModelSerializer):
    car_license = serializers.CharField(source='car.license_plate', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    days_to_expire = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = CarDocument
        fields = [
            'id', 'car', 'car_license', 'document_type', 'document_number',
            'issue_date', 'expiry_date', 'file_url', 'notes', 'is_expired',
            'days_to_expire', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CarListSerializer(serializers.ModelSerializer):
    model_name = serializers.CharField(source='model.name', read_only=True)
    brand_name = serializers.CharField(source='model.brand.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Car
        fields = [
            'id', 'brand_name', 'model_name', 'license_plate', 'color', 'status',
            'daily_price', 'is_available', 'primary_image', 'mileage', 'fuel_type',
            'transmission', 'seats'
        ]
    
    def get_primary_image(self, obj):
        primary = obj.images.filter(is_primary=True).first()
        return primary.image_url if primary else obj.image_url


class CarDetailSerializer(serializers.ModelSerializer):
    model_details = CarModelSerializer(source='model', read_only=True)
    images = CarImageSerializer(many=True, read_only=True)
    documents = CarDocumentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Car
        fields = [
            'id', 'model', 'model_details', 'license_plate', 'vin', 'color', 'status',
            'mileage', 'daily_price', 'is_available', 'fuel_type', 'transmission',
            'seats', 'doors', 'trunk_capacity', 'has_gps', 'has_air_conditioning',
            'has_power_steering', 'has_abs', 'has_airbag', 'description',
            'image_url', 'images', 'documents', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CarCreateUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Car
        fields = [
            'model', 'license_plate', 'vin', 'color', 'status', 'mileage',
            'daily_price', 'is_available', 'fuel_type', 'transmission',
            'seats', 'doors', 'trunk_capacity', 'has_gps', 'has_air_conditioning',
            'has_power_steering', 'has_abs', 'has_airbag', 'description', 'image_url'
        ]
    
    def validate_license_plate(self, value):
        if not value or len(value) < 5:
            raise serializers.ValidationError("License plate must be at least 5 characters.")
        return value.upper()
    
    def validate_vin(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("VIN must be at least 10 characters.")
        return value.upper()
    
    def validate_daily_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Daily rate must be greater than 0.")
        return value
