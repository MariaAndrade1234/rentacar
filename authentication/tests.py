from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import AuthToken, PasswordResetToken, LoginHistory
from .service.services import AuthService


class AuthenticationTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123',
            first_name='Test',
            last_name='User'
        )

    def test_user_registration(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'NewPassword123',
            'confirm_password': 'NewPassword123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_login(self):
        data = {
            'username': 'testuser',
            'password': 'TestPassword123'
        }
        response = self.client.post('/api/auth/login/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('refresh_token', response.data)

    def test_login_with_invalid_credentials(self):
        data = {
            'username': 'testuser',
            'password': 'WrongPassword'
        }
        response = self.client.post('/api/auth/login/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_verification(self):
        auth_token = AuthToken.generate_token(self.user)
        user = AuthService.verify_token(auth_token.token)
        self.assertEqual(user, self.user)

    def test_token_expiration(self):
        from django.utils import timezone
        from datetime import timedelta
        
        auth_token = AuthToken.generate_token(self.user)
        auth_token.expires_at = timezone.now() - timedelta(hours=1)
        auth_token.save()
        
        self.assertTrue(auth_token.is_expired())
        user = AuthService.verify_token(auth_token.token)
        self.assertIsNone(user)

    def test_password_change(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'old_password': 'TestPassword123',
            'new_password': 'NewPassword456',
            'confirm_password': 'NewPassword456'
        }
        response = self.client.post('/api/auth/password/change/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPassword456'))

    def test_password_reset_request(self):
        data = {'email': 'test@example.com'}
        response = self.client.post('/api/auth/password/reset/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(PasswordResetToken.objects.filter(user=self.user).exists())

    def test_password_reset_confirm(self):
        reset_token = PasswordResetToken.generate_token(self.user)
        data = {
            'token': reset_token.token,
            'new_password': 'ResetPassword789',
            'confirm_password': 'ResetPassword789'
        }
        response = self.client.post('/api/auth/password/reset/confirm/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('ResetPassword789'))

    def test_token_refresh(self):
        auth_token = AuthToken.generate_token(self.user)
        data = {'refresh_token': auth_token.refresh_token}
        response = self.client.post('/api/auth/token/refresh/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_logout(self):
        auth_token = AuthToken.generate_token(self.user)
        
        response = self.client.post(
            '/api/auth/logout/',
            HTTP_AUTHORIZATION=f'Bearer {auth_token.token}'
        )
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN])
        
        auth_token.refresh_from_db()
        self.assertFalse(auth_token.is_active)

    def test_login_history_tracking(self):
        data = {
            'username': 'testuser',
            'password': 'TestPassword123'
        }
        self.client.post('/api/auth/login/', data)
        self.assertTrue(LoginHistory.objects.filter(user=self.user, success=True).exists())

    def test_failed_login_tracking(self):
        data = {
            'username': 'testuser',
            'password': 'WrongPassword'
        }
        self.client.post('/api/auth/login/', data)
        self.assertTrue(LoginHistory.objects.filter(user=self.user, success=False).exists())
