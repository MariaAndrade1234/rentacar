from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from ..models import AuthToken, PasswordResetToken, LoginHistory
from ..validations.validation import (
    validate_login_data,
    validate_registration_data,
    validate_password_change
)


class AuthService:

    @staticmethod
    def login_user(username: str, password: str, ip_address=None, device_info=None, user_agent=None):
        validation = validate_login_data({'username': username, 'password': password})
        if not validation['valid']:
            LoginHistory.objects.create(
                user=User.objects.filter(username=username).first(),
                ip_address=ip_address,
                device_info=device_info,
                user_agent=user_agent,
                success=False,
                failure_reason='Invalid credentials'
            )
            raise ValidationError(validation['errors'])

        user = authenticate(username=username, password=password)
        
        if user is None:
            user_obj = User.objects.filter(username=username).first()
            if user_obj:
                LoginHistory.objects.create(
                    user=user_obj,
                    ip_address=ip_address,
                    device_info=device_info,
                    user_agent=user_agent,
                    success=False,
                    failure_reason='Invalid password'
                )
            return None

        if not user.is_active:
            LoginHistory.objects.create(
                user=user,
                ip_address=ip_address,
                device_info=device_info,
                user_agent=user_agent,
                success=False,
                failure_reason='Account is inactive'
            )
            return None

        auth_token = AuthToken.generate_token(
            user=user,
            device_info=device_info,
            ip_address=ip_address
        )

        LoginHistory.objects.create(
            user=user,
            ip_address=ip_address,
            device_info=device_info,
            user_agent=user_agent,
            success=True
        )

        return {
            'user': user,
            'token': auth_token.token,
            'refresh_token': auth_token.refresh_token,
            'expires_at': auth_token.expires_at,
        }

    @staticmethod
    def logout_user(token: str):
        try:
            auth_token = AuthToken.objects.get(token=token, is_active=True)
            auth_token.revoke()
            
            latest_login = LoginHistory.objects.filter(
                user=auth_token.user,
                success=True,
                logout_time__isnull=True
            ).first()
            
            if latest_login:
                latest_login.mark_logout()
            
            return True
        except AuthToken.DoesNotExist:
            return False

    @staticmethod
    def register_user(username: str, email: str, password: str, first_name='', last_name=''):
        validation = validate_registration_data({
            'username': username,
            'email': email,
            'password': password
        })
        
        if not validation['valid']:
            raise ValidationError(validation['errors'])

        if User.objects.filter(username=username).exists():
            raise ValidationError({'username': 'Username already exists'})

        if User.objects.filter(email=email).exists():
            raise ValidationError({'email': 'Email already exists'})

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            return user
        except Exception as e:
            raise Exception(f"Error creating user: {str(e)}")

    @staticmethod
    def change_password(user, old_password: str, new_password: str, confirm_password: str):
        validation = validate_password_change({
            'old_password': old_password,
            'new_password': new_password,
            'confirm_password': confirm_password
        })
        
        if not validation['valid']:
            raise ValidationError(validation['errors'])

        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            
            AuthToken.objects.filter(user=user, is_active=True).update(is_active=False)
            
            return True
        else:
            raise ValidationError({'old_password': 'Current password is incorrect'})

    @staticmethod
    def request_password_reset(email: str):
        try:
            user = User.objects.get(email=email, is_active=True)
            
            PasswordResetToken.objects.filter(
                user=user,
                is_used=False
            ).update(is_used=True, used_at=timezone.now())
            
            reset_token = PasswordResetToken.generate_token(user)
            
            return {
                'token': reset_token.token,
                'expires_at': reset_token.expires_at,
                'user': user
            }
        except User.DoesNotExist:
            return None

    @staticmethod
    def reset_password(token: str, new_password: str):
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
            
            if not reset_token.is_valid():
                raise ValidationError({'token': 'Token is invalid or expired'})
            
            user = reset_token.user
            user.set_password(new_password)
            user.save()
            
            reset_token.mark_as_used()
            
            AuthToken.objects.filter(user=user, is_active=True).update(is_active=False)
            
            return True
        except PasswordResetToken.DoesNotExist:
            raise ValidationError({'token': 'Invalid token'})

    @staticmethod
    def verify_token(token: str):
        try:
            auth_token = AuthToken.objects.get(token=token, is_active=True)
            
            if auth_token.is_expired():
                auth_token.revoke()
                return None
            
            return auth_token.user
        except AuthToken.DoesNotExist:
            return None

    @staticmethod
    def refresh_token(refresh_token: str, ip_address=None, device_info=None):
        try:
            auth_token = AuthToken.objects.get(refresh_token=refresh_token, is_active=True)
            
            if auth_token.is_refresh_expired():
                auth_token.revoke()
                return None
            
            auth_token.revoke()
            
            new_token = AuthToken.generate_token(
                user=auth_token.user,
                device_info=device_info or auth_token.device_info,
                ip_address=ip_address or auth_token.ip_address
            )
            
            return {
                'token': new_token.token,
                'refresh_token': new_token.refresh_token,
                'expires_at': new_token.expires_at,
            }
        except AuthToken.DoesNotExist:
            return None
