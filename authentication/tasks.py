import logging
from django.utils import timezone
from celery import shared_task
from .models import AuthToken, PasswordResetToken

logger = logging.getLogger(__name__)


@shared_task
def cleanup_expired_tokens():
  
    now = timezone.now()
    
    expired_auth_tokens = AuthToken.objects.filter(expires_at__lt=now)
    auth_count = expired_auth_tokens.count()
    expired_auth_tokens.delete()
    
    expired_reset_tokens = PasswordResetToken.objects.filter(expires_at__lt=now)
    reset_count = expired_reset_tokens.count()
    expired_reset_tokens.delete()
    
    logger.info(
        f"Token cleanup completed",
        extra={
            'auth_tokens_deleted': auth_count,
            'reset_tokens_deleted': reset_count
        }
    )
    
    return {
        'auth_tokens_deleted': auth_count,
        'reset_tokens_deleted': reset_count
    }


@shared_task
def cleanup_inactive_tokens():
   
    threshold_date = timezone.now() - timezone.timedelta(days=30)
    
    inactive_tokens = AuthToken.objects.filter(
        is_active=False,
        updated_at__lt=threshold_date
    )
    
    count = inactive_tokens.count()
    inactive_tokens.delete()
    
    logger.info(f"Cleaned up {count} inactive tokens")
    return {'deleted': count}
