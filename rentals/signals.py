import logging
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Rental, RentalPayment

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Rental)
def rental_created_or_updated(sender, instance, created, **kwargs):
    if created:
        logger.info(
            f"New rental created",
            extra={
                'rental_id': instance.id,
                'user_id': instance.user.id,
                'car_id': instance.car.id,
                'total_amount': float(instance.total_amount)
            }
        )
        
        if instance.status == 'CONFIRMED':
            instance.car.mark_as_rented()
            logger.info(f"Car {instance.car.id} marked as rented for rental {instance.id}")
    else:
        logger.info(
            f"Rental updated",
            extra={
                'rental_id': instance.id,
                'status': instance.status,
                'user_id': instance.user.id
            }
        )
    
    cache_key = f'user_rentals_{instance.user.id}'
    cache.delete(cache_key)
    
    cache_key = f'car_availability_{instance.car.id}'
    cache.delete(cache_key)


@receiver(pre_save, sender=Rental)
def rental_status_changed(sender, instance, **kwargs):
    if instance.pk: 
        try:
            old_rental = Rental.objects.get(pk=instance.pk)

            if old_rental.status != instance.status:
                logger.info(
                    f"Rental status changed",
                    extra={
                        'rental_id': instance.id,
                        'old_status': old_rental.status,
                        'new_status': instance.status,
                        'user_id': instance.user.id
                    }
                )
                
                if instance.status in ['COMPLETED', 'CANCELLED']:
                    instance.car.mark_as_available()
                    logger.info(f"Car {instance.car.id} marked as available (rental {instance.status})")
        except Rental.DoesNotExist:
            pass


@receiver(post_save, sender=RentalPayment)
def payment_processed(sender, instance, created, **kwargs):

    if created:
        logger.info(
            f"Payment created",
            extra={
                'payment_id': instance.id,
                'rental_id': instance.rental.id,
                'amount': float(instance.amount),
                'method': instance.payment_method,
                'status': instance.status
            }
        )
    
    if instance.status == 'COMPLETED':
        rental = instance.rental
        if rental.status == 'PENDING':
            rental.status = 'CONFIRMED'
            rental.save()
            logger.info(f"Rental {rental.id} confirmed after payment completion")


@receiver(post_delete, sender=Rental)
def rental_deleted(sender, instance, **kwargs):

    logger.warning(
        f"Rental deleted",
        extra={
            'rental_id': instance.id,
            'user_id': instance.user.id,
            'car_id': instance.car.id
        }
    )
    
    cache_key = f'user_rentals_{instance.user.id}'
    cache.delete(cache_key)
