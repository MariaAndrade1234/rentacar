from django.urls import path
from .views import (
    LoginView, LogoutView, RegisterView,
    PasswordChangeView, PasswordResetRequestView, PasswordResetConfirmView,
    RefreshTokenView, LoginHistoryView
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='auth-login'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('password/change/', PasswordChangeView.as_view(), name='auth-password-change'),
    path('password/reset/', PasswordResetRequestView.as_view(), name='auth-password-reset'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='auth-password-reset-confirm'),
    path('token/refresh/', RefreshTokenView.as_view(), name='auth-token-refresh'),
    path('history/', LoginHistoryView.as_view(), name='auth-login-history'),
]
