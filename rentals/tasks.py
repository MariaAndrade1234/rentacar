"""
Celery tasks for rentals app.
Handles asynchronous operations like notifications, reports, and cleanup.
"""

import logging
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task
from .models import Rental
from core.exceptions import RentalException

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_rental_confirmation_email(self, rental_id: int):
    """
    Send confirmation email to user when rental is created.
    """
    try:
        rental = Rental.objects.select_related('user', 'car__model__brand').get(id=rental_id)
        
        subject = f'Rental Confirmation - {rental.car.model.brand.name} {rental.car.model.name}'
        message = f"""
        Dear {rental.user.first_name},
        
        Your rental has been confirmed!
        
        Car: {rental.car.model.brand.name} {rental.car.model.name}
        License Plate: {rental.car.license_plate}
        Pickup Date: {rental.start_date.strftime('%Y-%m-%d %H:%M')}
        Return Date: {rental.end_date.strftime('%Y-%m-%d %H:%M')}
        Total Amount: ${rental.total_amount}
        
        Pickup Location: {rental.pickup_location}
        
        Thank you for choosing RentACar!
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [rental.user.email],
            fail_silently=False,
        )
        
        logger.info(f"Confirmation email sent for rental {rental_id}")
        return {'success': True, 'rental_id': rental_id}
        
    except Rental.DoesNotExist:
        logger.error(f"Rental {rental_id} not found")
        raise
    except Exception as exc:
        logger.error(f"Failed to send email for rental {rental_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)  # Retry after 1 minute


@shared_task(bind=True, max_retries=3)
def send_rental_reminder(self, rental_id: int):
    """
    Send reminder email 24 hours before rental starts.
    """
    try:
        rental = Rental.objects.select_related('user', 'car__model__brand').get(id=rental_id)
        
        subject = 'Rental Reminder - Your rental starts tomorrow'
        message = f"""
        Dear {rental.user.first_name},
        
        This is a reminder that your rental starts tomorrow!
        
        Car: {rental.car.model.brand.name} {rental.car.model.name}
        Pickup Time: {rental.start_date.strftime('%Y-%m-%d %H:%M')}
        Pickup Location: {rental.pickup_location}
        
        Please arrive 15 minutes early to complete the paperwork.
        
        See you soon!
        RentACar Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [rental.user.email],
            fail_silently=False,
        )
        
        logger.info(f"Reminder email sent for rental {rental_id}")
        return {'success': True, 'rental_id': rental_id}
        
    except Exception as exc:
        logger.error(f"Failed to send reminder for rental {rental_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=300)


@shared_task
def check_overdue_rentals():
    """
    Check for overdue rentals and send notifications.
    Runs hourly via Celery Beat.
    """
    now = timezone.now()
    overdue_rentals = Rental.objects.filter(
        status='ACTIVE',
        end_date__lt=now
    ).select_related('user', 'car')
    
    count = 0
    for rental in overdue_rentals:
        # Calculate late fees
        days_late = (now - rental.end_date).days
        late_fee = Decimal(days_late) * Decimal('50.00')  # $50 per day
        
        logger.warning(
            f"Overdue rental detected",
            extra={
                'rental_id': rental.id,
                'user_id': rental.user.id,
                'days_late': days_late,
                'late_fee': float(late_fee)
            }
        )
        
        # Send notification email
        try:
            send_mail(
                'Overdue Rental Notice',
                f"Your rental is {days_late} day(s) overdue. Late fee: ${late_fee}",
                settings.DEFAULT_FROM_EMAIL,
                [rental.user.email],
                fail_silently=True,
            )
            count += 1
        except Exception as e:
            logger.error(f"Failed to send overdue notice for rental {rental.id}: {str(e)}")
    
    logger.info(f"Checked overdue rentals: {count} notifications sent")
    return {'checked': overdue_rentals.count(), 'notified': count}


@shared_task
def generate_daily_reports():
    """
    Generate daily statistics and reports.
    Runs daily at 11:30 PM via Celery Beat.
    """
    today = timezone.now().date()
    
    # Get today's statistics
    rentals_created = Rental.objects.filter(created_at__date=today).count()
    rentals_completed = Rental.objects.filter(
        status='COMPLETED',
        actual_return_date__date=today
    ).count()
    
    total_revenue = sum(
        rental.total_amount for rental in 
        Rental.objects.filter(
            status='COMPLETED',
            actual_return_date__date=today
        )
    )
    
    logger.info(
        f"Daily report generated",
        extra={
            'date': str(today),
            'rentals_created': rentals_created,
            'rentals_completed': rentals_completed,
            'total_revenue': float(total_revenue)
        }
    )
    
    return {
        'date': str(today),
        'rentals_created': rentals_created,
        'rentals_completed': rentals_completed,
        'total_revenue': float(total_revenue)
    }


@shared_task(bind=True)
def process_rental_cancellation(self, rental_id: int, refund_amount: Decimal):
    """
    Process rental cancellation and refund asynchronously.
    """
    try:
        rental = Rental.objects.get(id=rental_id)
        
        # Process refund (integrate with payment gateway)
        # This is a placeholder - integrate with real payment processor
        logger.info(
            f"Processing refund",
            extra={
                'rental_id': rental_id,
                'refund_amount': float(refund_amount)
            }
        )
        
        # Send cancellation email
        send_mail(
            'Rental Cancellation Confirmation',
            f"Your rental has been cancelled. Refund amount: ${refund_amount}",
            settings.DEFAULT_FROM_EMAIL,
            [rental.user.email],
            fail_silently=False,
        )
        
        logger.info(f"Cancellation processed for rental {rental_id}")
        return {'success': True, 'rental_id': rental_id, 'refund': float(refund_amount)}
        
    except Exception as exc:
        logger.error(f"Failed to process cancellation for rental {rental_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=120)
