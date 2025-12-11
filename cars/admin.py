from django.contrib import admin
from .models import CarBrand, CarModel, Car, CarDocument, CarImage


@admin.register(CarBrand)
class CarBrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'created_at']
    search_fields = ['name', 'country']
    list_filter = ['country']
    ordering = ['name']


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'year']
    search_fields = ['name', 'brand__name']
    list_filter = ['brand', 'year']
    ordering = ['brand', '-year', 'name']


class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 1


class CarDocumentInline(admin.TabularInline):
    model = CarDocument
    extra = 0


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['license_plate', 'model', 'color', 'status', 'daily_price', 'is_available', 'mileage']
    search_fields = ['license_plate', 'vin', 'model__name', 'model__brand__name']
    list_filter = ['status', 'is_available', 'model__brand', 'fuel_type']
    ordering = ['model__brand__name', 'model__name']
    inlines = [CarImageInline, CarDocumentInline]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('model', 'license_plate', 'vin', 'color', 'status')
        }),
        ('Especificações', {
            'fields': ('mileage', 'fuel_type', 'transmission', 'seats', 'doors', 'trunk_capacity')
        }),
        ('Recursos', {
            'fields': ('has_gps', 'has_air_conditioning', 'has_power_steering', 'has_abs', 'has_airbag')
        }),
        ('Preço & Disponibilidade', {
            'fields': ('daily_price', 'is_available')
        }),
        ('Mídia & Descrição', {
            'fields': ('image_url', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CarDocument)
class CarDocumentAdmin(admin.ModelAdmin):
    list_display = ['car', 'document_type', 'document_number', 'expiry_date', 'is_expired']
    search_fields = ['car__license_plate', 'document_number']
    list_filter = ['document_type']
    ordering = ['-expiry_date']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CarImage)
class CarImageAdmin(admin.ModelAdmin):
    list_display = ['car', 'is_primary', 'created_at']
    search_fields = ['car__license_plate']
    list_filter = ['is_primary']
    ordering = ['-created_at']
