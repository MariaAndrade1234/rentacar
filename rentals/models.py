from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta


class Rental(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rentals')
    car = models.ForeignKey('cars.Car', on_delete=models.PROTECT, related_name='rentals')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    actual_return_date = models.DateTimeField(null=True, blank=True)
    
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    total_days = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    
    mileage_start = models.PositiveIntegerField(null=True, blank=True)
    mileage_end = models.PositiveIntegerField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rentals'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['car', '-created_at']),
        ]
    
    def __str__(self):
        return f"Rental #{self.id} - {self.user.username} - {self.car.license_plate}"
    
    def calculate_total_amount(self):
        self.total_days = (self.end_date - self.start_date).days or 1
        self.subtotal = self.daily_rate * self.total_days
        self.total_amount = self.subtotal - self.discount + self.tax
        return self.total_amount
    
    def is_overdue(self):
        if self.status == 'ACTIVE' and self.end_date < timezone.now():
            return True
        return False
    
    def get_duration_days(self):
        return (self.end_date - self.start_date).days
    
    def get_actual_duration_days(self):
        if self.actual_return_date:
            return (self.actual_return_date - self.start_date).days
        return None


class RentalPayment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('CREDIT_CARD', 'Credit Card'),
        ('DEBIT_CARD', 'Debit Card'),
        ('CASH', 'Cash'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('PIX', 'PIX'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]
    
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rental_payments'
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"Payment #{self.id} - Rental #{self.rental.id} - {self.amount}"


class RentalReview(models.Model):
    rental = models.OneToOneField(Rental, on_delete=models.CASCADE, related_name='review')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rental_reviews'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review for Rental #{self.rental.id} - {self.rating}/5"


class RentalDocument(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('CONTRACT', 'Rental Contract'),
        ('INSPECTION_BEFORE', 'Inspection Before'),
        ('INSPECTION_AFTER', 'Inspection After'),
        ('INVOICE', 'Invoice'),
        ('RECEIPT', 'Receipt'),
        ('OTHER', 'Other'),
    ]
    
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    file_url = models.URLField(max_length=500)
    description = models.CharField(max_length=255, blank=True)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'rental_documents'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.get_document_type_display()} - Rental #{self.rental.id}"
