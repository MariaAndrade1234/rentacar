from django.contrib import admin
from .models import Rental, RentalPayment, RentalReview, RentalDocument


class RentalPaymentInline(admin.TabularInline):
    model = RentalPayment
    extra = 0
    readonly_fields = ['payment_date']


class RentalDocumentInline(admin.TabularInline):
    model = RentalDocument
    extra = 0
    readonly_fields = ['uploaded_at']


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'car', 'start_date', 'end_date', 'status', 'total_amount', 'created_at']
    search_fields = ['user__username', 'car__license_plate', 'pickup_location', 'dropoff_location']
    list_filter = ['status', 'start_date', 'end_date']
    ordering = ['-created_at']
    inlines = [RentalPaymentInline, RentalDocumentInline]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('user',)
        }),
        ('Vehicle Information', {
            'fields': ('car',)
        }),
        ('Dates & Location', {
            'fields': ('start_date', 'end_date', 'actual_return_date', 'pickup_location', 'dropoff_location')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Amounts', {
            'fields': ('daily_rate', 'total_days', 'subtotal', 'discount', 'tax', 'total_amount')
        }),
        ('Mileage', {
            'fields': ('mileage_start', 'mileage_end')
        }),
        ('Notes', {
            'fields': ('notes', 'cancellation_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RentalPayment)
class RentalPaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'rental', 'amount', 'payment_method', 'status', 'payment_date']
    search_fields = ['rental__id', 'transaction_id']
    list_filter = ['status', 'payment_method', 'payment_date']
    ordering = ['-payment_date']
    readonly_fields = ['payment_date', 'created_at', 'updated_at']


@admin.register(RentalReview)
class RentalReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'rental', 'rating', 'created_at']
    search_fields = ['rental__id', 'rental__user__username']
    list_filter = ['rating', 'created_at']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(RentalDocument)
class RentalDocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'rental', 'document_type', 'uploaded_at']
    search_fields = ['rental__id', 'description']
    list_filter = ['document_type', 'uploaded_at']
    ordering = ['-uploaded_at']
    readonly_fields = ['uploaded_at']

