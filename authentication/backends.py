from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from .models import AuthToken


class TokenAuthenticationBackend(ModelBackend):

    def authenticate(self, request, token=None, **kwargs):
        if token is None:
            return None

        try:
            auth_token = AuthToken.objects.get(token=token, is_active=True)
            
            if auth_token.is_expired():
                auth_token.revoke()
                return None
            
            return auth_token.user
        except AuthToken.DoesNotExist:
            return None

    def get_user(self, user_id):
       
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
