"""
Tests for the Auth app.

Covers the registration/user serializers, every authentication API endpoint
(csrf, signin, register, logout, init, user-update), and the protections on
the anonymous ones: CSRF, the per-account lockout and the per-IP rate limits.
"""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from apps.auth.api import views as auth_views
from apps.auth.api.serializers import RegisterSerializer, UserSerializer
from apps.auth.api.throttles import LoginRateThrottle, RegisterRateThrottle

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
        self.assertEqual(data['username'], 'carol')

    def test_name_uses_full_name_when_available(self):
        user = User.objects.create_user(
            username='dave', password='whatever123',
            first_name='Dave', last_name='Smith',
        )
        data = UserSerializer(user).data
        self.assertEqual(data['name'], 'Dave Smith')

    def test_username_is_writable(self):
        user = User.objects.create_user(username='erin', password='whatever123')
        serializer = UserSerializer(user, data={'username': 'erin2'}, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated = serializer.save()
        self.assertEqual(updated.username, 'erin2')


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


class CsrfProtectionTests(APITestCase):
    """Sign-in and register refuse a cross-site request.

    DRF's @api_view exempts views from Django's CSRF middleware and only
    re-checks it for an already-authenticated session, so without the views'
    csrf_protect an attacker's page could sign a visitor into an account the
    attacker controls (login CSRF).
    """

    def setUp(self):
        cache.clear()
        self.client = self.client_class(enforce_csrf_checks=True)
        User.objects.create_user(username='kim', password='correct-horse-9')

    def _csrf_token(self):
        self.client.get(reverse('auth_api:csrf'))
        return self.client.cookies['csrftoken'].value

    def test_signin_without_a_csrf_token_is_rejected(self):
        resp = self.client.post(
            reverse('auth_api:signin'),
            {'username': 'kim', 'password': 'correct-horse-9'},
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_register_without_a_csrf_token_is_rejected(self):
        resp = self.client.post(reverse('auth_api:register'), {
            'username': 'lee',
            'email': 'lee@example.com',
            'password': 'sup3rSecret!',
            'password_confirmation': 'sup3rSecret!',
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(User.objects.filter(username='lee').exists())

    def test_signin_with_the_csrf_token_succeeds(self):
        token = self._csrf_token()
        resp = self.client.post(
            reverse('auth_api:signin'),
            {'username': 'kim', 'password': 'correct-horse-9'},
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


# The per-IP throttle is lifted for the lockout tests so that only the
# per-account counter is under test.
@patch.object(LoginRateThrottle, 'THROTTLE_RATES', {'auth_signin': '1000/min'})
class FailedLoginLockoutTests(APITestCase):
    """Repeated failures against one account are refused for a while."""

    def setUp(self):
        cache.clear()
        self.url = reverse('auth_api:signin')
        self.user = User.objects.create_user(username='mia', password='correct-horse-9')

    def _fail(self, times, username='mia'):
        for _ in range(times):
            self.client.post(self.url, {'username': username, 'password': 'wrong'})

    def test_account_is_locked_after_the_failure_limit(self):
        self._fail(auth_views.FAILED_LOGIN_LIMIT)
        # Even the right password is refused while locked.
        resp = self.client.post(
            self.url, {'username': 'mia', 'password': 'correct-horse-9'}
        )
        self.assertEqual(resp.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertFalse(Token.objects.filter(user=self.user).exists())

    def test_lockout_ignores_username_case_and_whitespace(self):
        self._fail(auth_views.FAILED_LOGIN_LIMIT, username=' MIA ')
        resp = self.client.post(
            self.url, {'username': 'mia', 'password': 'correct-horse-9'}
        )
        self.assertEqual(resp.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_a_success_clears_earlier_failures(self):
        self._fail(auth_views.FAILED_LOGIN_LIMIT - 1)
        ok = self.client.post(self.url, {'username': 'mia', 'password': 'correct-horse-9'})
        self.assertEqual(ok.status_code, status.HTTP_200_OK)
        self._fail(auth_views.FAILED_LOGIN_LIMIT - 1)
        again = self.client.post(self.url, {'username': 'mia', 'password': 'correct-horse-9'})
        self.assertEqual(again.status_code, status.HTTP_200_OK)

    def test_failures_on_one_account_do_not_lock_another(self):
        User.objects.create_user(username='noah', password='correct-horse-9')
        self._fail(auth_views.FAILED_LOGIN_LIMIT)
        resp = self.client.post(
            self.url, {'username': 'noah', 'password': 'correct-horse-9'}
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_cache_key_never_contains_the_username(self):
        key = auth_views._failed_login_key('mia')
        self.assertNotIn('mia', key)
        self.assertEqual(key, auth_views._failed_login_key(' MIA '))


class RateLimitTests(APITestCase):
    """Per-IP caps on the anonymous credential endpoints."""

    def setUp(self):
        cache.clear()

    @patch.object(LoginRateThrottle, 'THROTTLE_RATES', {'auth_signin': '3/min'})
    def test_signin_is_rate_limited_per_ip(self):
        url = reverse('auth_api:signin')
        codes = [
            self.client.post(url, {'username': f'user{i}', 'password': 'wrong'}).status_code
            for i in range(4)
        ]
        self.assertEqual(codes[:3], [status.HTTP_401_UNAUTHORIZED] * 3)
        self.assertEqual(codes[3], status.HTTP_429_TOO_MANY_REQUESTS)

    @patch.object(RegisterRateThrottle, 'THROTTLE_RATES', {'auth_register': '1/hour'})
    def test_register_is_rate_limited_per_ip(self):
        url = reverse('auth_api:register')
        payload = {
            'email': 'x@example.com',
            'password': 'sup3rSecret!',
            'password_confirmation': 'sup3rSecret!',
        }
        first = self.client.post(url, {**payload, 'username': 'first'})
        second = self.client.post(
            url, {**payload, 'username': 'second', 'email': 'y@example.com'}
        )
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    @patch.object(LoginRateThrottle, 'THROTTLE_RATES', {})
    def test_a_missing_rate_setting_falls_back_to_the_default(self):
        # A project whose settings name no rate keeps its limit rather than
        # failing every sign-in with ImproperlyConfigured.
        self.assertEqual(LoginRateThrottle().rate, LoginRateThrottle.default_rate)

