from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import secrets


class AuthToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auth_tokens')
    token = models.CharField(max_length=255, unique=True, db_index=True)
    refresh_token = models.CharField(max_length=255, unique=True, null=True, blank=True)
    expires_at = models.DateTimeField()
    refresh_expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    device_info = models.CharField(max_length=255, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        db_table = 'auth_tokens'
        ordering = ['-created_at']
        verbose_name = 'Authentication Token'
        verbose_name_plural = 'Authentication Tokens'

    def __str__(self):
        return f"Token for {self.user.username} - {self.created_at}"

    def is_expired(self):
        return timezone.now() > self.expires_at

    def is_refresh_expired(self):
        if self.refresh_expires_at:
            return timezone.now() > self.refresh_expires_at
        return True

    @classmethod
    def generate_token(cls, user, device_info=None, ip_address=None):
        token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=24)
        refresh_expires_at = timezone.now() + timedelta(days=30)

        auth_token = cls.objects.create(
            user=user,
            token=token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            refresh_expires_at=refresh_expires_at,
            device_info=device_info,
            ip_address=ip_address
        )
        return auth_token

    def revoke(self):
        self.is_active = False
        self.save()


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'password_reset_tokens'
        ordering = ['-created_at']
        verbose_name = 'Password Reset Token'
        verbose_name_plural = 'Password Reset Tokens'

    def __str__(self):
        return f"Password reset for {self.user.username} - {self.created_at}"

    def is_expired(self):
        return timezone.now() > self.expires_at

    def is_valid(self):
        return not self.is_used and not self.is_expired()

    @classmethod
    def generate_token(cls, user):
        token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=1)

        reset_token = cls.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
        return reset_token

    def mark_as_used(self):
        self.is_used = True
        self.used_at = timezone.now()
        self.save()


class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    device_info = models.CharField(max_length=255, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    success = models.BooleanField(default=True)
    failure_reason = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'login_history'
        ordering = ['-login_time']
        verbose_name = 'Login History'
        verbose_name_plural = 'Login Histories'

    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"{self.user.username} - {status} - {self.login_time}"

    def mark_logout(self):
        self.logout_time = timezone.now()
        self.save()
