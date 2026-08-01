"""Tests for the ops/diagnostic endpoints."""

from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse


class VersionInfoBinariesTests(TestCase):
    """The version endpoint reports the workspace's external programs.

    These exist because a missing binary is invisible everywhere else: the
    image installs git/node/npm/chromium on purpose, the developer's machine
    has them anyway, and nothing in the test suite runs inside the image. When
    git went missing in production, the only symptom was subagents that never
    said anything.
    """

    def test_reports_binaries_that_are_present(self):
        response = self.client.get(reverse('home_ops:version_web'))
        self.assertEqual(response.status_code, 200)
        body = response.json()
        # Whatever this machine has, the two fields must agree with each other.
        self.assertIn('binaries', body)
        self.assertEqual(
            body['missing_binaries'],
            sorted(name for name, path in body['binaries'].items() if not path),
        )

    def test_missing_binary_is_named(self):
        """A binary that is not on PATH is listed, not silently omitted."""
        with patch('apps.Home.api.views.shutil.which', return_value=None):
            body = self.client.get(reverse('home_ops:version_web')).json()

        self.assertIn('git', body['missing_binaries'])
        self.assertIsNone(body['binaries']['git'])

    def test_env_pinned_binary_is_checked_at_its_pinned_path(self):
        """chromium is found by env var, not PATH — a stale pin reads missing."""
        with patch.dict(
            'os.environ', {'BROWSER_PREVIEW_EXECUTABLE': '/nope/chromium'}
        ):
            body = self.client.get(reverse('home_ops:version_web')).json()

        self.assertIn('chromium', body['missing_binaries'])

    def test_missing_binaries_is_empty_when_all_present(self):
        with patch(
            'apps.Home.api.views.shutil.which', side_effect=lambda n: f'/usr/bin/{n}'
        ), patch.dict(
            'os.environ', {'BROWSER_PREVIEW_EXECUTABLE': __file__}
        ):
            body = self.client.get(reverse('home_ops:version_web')).json()

        self.assertEqual(body['missing_binaries'], [])

    def test_both_tiers_answer(self):
        """Same view under both prefixes: you can compare web against workspace."""
        for name in ('home_ops:version_web', 'home_ops:version_workspace'):
            with self.subTest(route=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)
                self.assertIn('missing_binaries', response.json())


class DatabaseStatusDisclosureTests(TestCase):
    """The health endpoints are AllowAny, so a DB error must not describe itself.

    A libpq connection failure names the internal database host, its resolved
    address, the port and the role — exactly what an unauthenticated caller
    should not learn, and available precisely when the deployment is degraded.
    """

    def test_healthy_database_reports_connected(self):
        response = self.client.get(reverse('home_api:health_check'))
        self.assertEqual(response.json()['database'], 'connected')

    def test_database_error_is_not_described_to_the_caller(self):
        boom = Exception(
            'connection to server at "postgres.railway.internal" (fd12::1), '
            'port 5432 failed: FATAL: password authentication failed for user "postgres"'
        )
        with patch('apps.Home.api.views.get_user_model') as get_model:
            get_model.return_value.objects.exists.side_effect = boom
            response = self.client.get(reverse('home_api:health_check'))

        body = response.json()
        self.assertEqual(body['database'], 'error')
        serialized = str(body)
        self.assertNotIn('postgres.railway.internal', serialized)
        self.assertNotIn('5432', serialized)
        self.assertNotIn('password authentication', serialized)
