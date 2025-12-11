from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class CarBrand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    logo_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'

    def __str__(self):
        return self.name


class CarModel(models.Model):
    brand = models.ForeignKey(CarBrand, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=100)
    year = models.IntegerField(validators=[MinValueValidator(2000), MaxValueValidator(2100)])
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year', 'name']
        verbose_name = 'Modelo'
        verbose_name_plural = 'Modelos'
        unique_together = ['brand', 'name', 'year']

    def __str__(self):
        return f"{self.brand.name} {self.name} ({self.year})"


class Car(models.Model):
    
    FUEL_CHOICES = [
        ('GASOLINE', 'Gasolina'),
        ('DIESEL', 'Diesel'),
        ('HYBRID', 'Híbrido'),
        ('ELECTRIC', 'Elétrico'),
    ]
    
    TRANSMISSION_CHOICES = [
        ('MANUAL', 'Manual'),
        ('AUTOMATIC', 'Automático'),
    ]
    
    STATUS_CHOICES = [
        ('AVAILABLE', 'Disponível'),
        ('RENTED', 'Alugado'),
        ('MAINTENANCE', 'Em Manutenção'),
        ('DAMAGED', 'Danificado'),
        ('RETIRED', 'Desativado'),
    ]
    
    model = models.ForeignKey(CarModel, on_delete=models.CASCADE, related_name='cars')
    license_plate = models.CharField(max_length=20, unique=True)
    vin = models.CharField(max_length=50, unique=True, verbose_name='VIN')
    color = models.CharField(max_length=50)
    mileage = models.IntegerField(validators=[MinValueValidator(0)])
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES)
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES)
    seats = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(9)])
    doors = models.IntegerField(validators=[MinValueValidator(2), MaxValueValidator(5)])
    trunk_capacity = models.IntegerField(help_text='Capacidade do porta-malas em litros')
    daily_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    is_available = models.BooleanField(default=True)
    has_gps = models.BooleanField(default=False)
    has_air_conditioning = models.BooleanField(default=True)
    has_power_steering = models.BooleanField(default=True)
    has_abs = models.BooleanField(default=True)
    has_airbag = models.BooleanField(default=True)
    image_url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['model']
        verbose_name = 'Carro'
        verbose_name_plural = 'Carros'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['is_available']),
            models.Index(fields=['daily_price']),
        ]

    def __str__(self):
        return f"{self.model} - {self.license_plate}"

    def mark_as_rented(self):
        self.status = 'RENTED'
        self.is_available = False
        self.save()

    def mark_as_available(self):
        self.status = 'AVAILABLE'
        self.is_available = True
        self.save()

    def mark_for_maintenance(self):
        self.status = 'MAINTENANCE'
        self.is_available = False
        self.save()

    def mark_as_damaged(self):
        self.status = 'DAMAGED'
        self.is_available = False
        self.save()


class CarDocument(models.Model):
    
    DOCUMENT_TYPES = [
        ('REGISTRATION', 'Registro'),
        ('INSURANCE', 'Seguro'),
        ('INSPECTION', 'Vistoria'),
        ('TAX', 'IPVA'),
        ('MAINTENANCE', 'Manutenção'),
        ('OTHER', 'Outro'),
    ]
    
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    document_number = models.CharField(max_length=100)
    issue_date = models.DateField()
    expiry_date = models.DateField()
    file_url = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-expiry_date']
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'

    def __str__(self):
        return f"{self.car} - {self.get_document_type_display()}"

    @property
    def is_expired(self):
        return self.expiry_date < timezone.now().date()

    @property
    def days_to_expire(self):
        delta = self.expiry_date - timezone.now().date()
        return delta.days


class CarImage(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField()
    description = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', '-created_at']
        verbose_name = 'Imagem'
        verbose_name_plural = 'Imagens'

    def __str__(self):
        return f"Imagem - {self.car.license_plate}"
