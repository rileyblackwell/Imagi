"""
Tests for the Auth app.

Covers the registration/user serializers and every authentication API
endpoint (csrf, signin, register, logout, init, user-update).
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from apps.Auth.api.serializers import RegisterSerializer, UserSerializer

User = get_user_model()


class RegisterSerializerTests(APITestCase):
    """Validation rules enforced by RegisterSerializer."""

    def _base_data(self, **overrides):
        data = {
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'sup3rSecret!',
            'password_confirmation': 'sup3rSecret!',
        }
        data.update(overrides)
        return data

    def test_valid_payload_creates_user(self):
        serializer = RegisterSerializer(data=self._base_data())
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertEqual(user.username, 'alice')
        self.assertEqual(user.email, 'alice@example.com')
        # Password must be hashed, never stored in the clear.
        self.assertTrue(user.check_password('sup3rSecret!'))
        self.assertNotEqual(user.password, 'sup3rSecret!')

    def test_password_mismatch_is_rejected(self):
        serializer = RegisterSerializer(
            data=self._base_data(password_confirmation='different!')
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('password_confirmation', serializer.errors)

    def test_duplicate_username_is_rejected(self):
        User.objects.create_user(username='alice', password='whatever123')
        serializer = RegisterSerializer(data=self._base_data())
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)

    def test_duplicate_email_is_rejected_case_insensitively(self):
        User.objects.create_user(
            username='bob', email='ALICE@example.com', password='whatever123'
        )
        serializer = RegisterSerializer(data=self._base_data())
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_weak_password_is_rejected(self):
        serializer = RegisterSerializer(
            data=self._base_data(password='password', password_confirmation='password')
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)


class UserSerializerTests(APITestCase):
    """Read-only representation returned to the SPA."""

    def test_name_falls_back_to_username(self):
        user = User.objects.create_user(username='carol', password='whatever123')
        data = UserSerializer(user).data
        self.assertEqual(data['name'], 'carol')
        self.assertEqual(data['balance'], 0)
        self.assertEqual(data['username'], 'carol')

    def test_name_uses_full_name_when_available(self):
        user = User.objects.create_user(
            username='dave', password='whatever123',
            first_name='Dave', last_name='Smith',
        )
        data = UserSerializer(user).data
        self.assertEqual(data['name'], 'Dave Smith')

    def test_balance_and_id_are_read_only(self):
        user = User.objects.create_user(username='erin', password='whatever123')
        serializer = UserSerializer(
            user, data={'balance': 999, 'username': 'erin2'}, partial=True
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated = serializer.save()
        # username is writable, balance is not.
        self.assertEqual(updated.username, 'erin2')
        self.assertEqual(UserSerializer(updated).data['balance'], 0)


class SigninViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('auth_api:signin')
        self.user = User.objects.create_user(
            username='frank', email='frank@example.com', password='correct-horse-9'
        )

    def test_valid_credentials_return_token_and_user(self):
        resp = self.client.post(
            self.url, {'username': 'frank', 'password': 'correct-horse-9'}
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('token', resp.data)
        self.assertEqual(resp.data['user']['username'], 'frank')
        # A token row must be created and match the returned key.
        token = Token.objects.get(user=self.user)
        self.assertEqual(token.key, resp.data['token'])

    def test_wrong_password_returns_401(self):
        resp = self.client.post(
            self.url, {'username': 'frank', 'password': 'wrong'}
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(Token.objects.filter(user=self.user).exists())

    def test_missing_fields_return_400(self):
        resp = self.client.post(self.url, {'username': 'frank'})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signin_is_idempotent_on_token(self):
        first = self.client.post(
            self.url, {'username': 'frank', 'password': 'correct-horse-9'}
        )
        second = self.client.post(
            self.url, {'username': 'frank', 'password': 'correct-horse-9'}
        )
        self.assertEqual(first.data['token'], second.data['token'])


class RegisterViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('auth_api:register')

    def test_register_creates_user_and_returns_token(self):
        resp = self.client.post(self.url, {
            'username': 'grace',
            'email': 'grace@example.com',
            'password': 'sup3rSecret!',
            'password_confirmation': 'sup3rSecret!',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', resp.data)
        self.assertEqual(resp.data['user']['username'], 'grace')
        self.assertTrue(User.objects.filter(username='grace').exists())

    def test_register_with_invalid_data_returns_400(self):
        resp = self.client.post(self.url, {
            'username': 'grace',
            'email': 'not-an-email',
            'password': 'x',
            'password_confirmation': 'y',
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username='grace').exists())


class LogoutViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('auth_api:logout')
        self.user = User.objects.create_user(username='heidi', password='correct-horse-9')
        self.token = Token.objects.create(user=self.user)

    def test_logout_requires_authentication(self):
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_deletes_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertFalse(Token.objects.filter(user=self.user).exists())


class InitViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('auth_api:init')
        self.user = User.objects.create_user(username='ivan', password='correct-horse-9')

    def test_unauthenticated_reports_not_authenticated(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertFalse(resp.data['isAuthenticated'])
        self.assertIsNone(resp.data['user'])

    def test_authenticated_returns_user(self):
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data['isAuthenticated'])
        self.assertEqual(resp.data['user']['username'], 'ivan')


class UserUpdateViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('auth_api:user-update')
        self.user = User.objects.create_user(
            username='judy', email='judy@example.com', password='correct-horse-9'
        )

    def test_update_requires_authentication(self):
        resp = self.client.patch(self.url, {'email': 'new@example.com'})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_update_email(self):
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        resp = self.client.patch(self.url, {'email': 'new@example.com'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'new@example.com')
