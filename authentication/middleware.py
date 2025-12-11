from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin
from .service.services import AuthService


class TokenAuthenticationMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request.user = AnonymousUser()
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '')
            user = AuthService.verify_token(token)
            
            if user:
                request.user = user
