from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.test import SimpleTestCase, override_settings

from apps.Imagi.Build.management.commands import migrate_locked


class MigrateLockedTests(SimpleTestCase):
    """Both production tiers migrate on boot through this command; on Postgres
    the advisory lock is what stops them racing the same migration."""

    def _run(self, vendor):
        cursor = mock.MagicMock()
        connection = mock.MagicMock(vendor=vendor)
        connection.cursor.return_value.__enter__.return_value = cursor
        with mock.patch.object(migrate_locked, 'connections', {'default': connection}), \
                mock.patch.object(migrate_locked, 'call_command') as migrate:
            call_command('migrate_locked', stdout=StringIO())
        return cursor, migrate

    def test_postgres_migrates_and_reencrypts_inside_the_advisory_lock(self):
        order = []
        cursor = mock.MagicMock()
        cursor.execute.side_effect = lambda sql, params: order.append(sql.split('(')[0])
        connection = mock.MagicMock(vendor='postgresql')
        connection.cursor.return_value.__enter__.return_value = cursor
        with mock.patch.object(migrate_locked, 'connections', {'default': connection}), \
                mock.patch.object(migrate_locked, 'call_command',
                                  side_effect=lambda name, **k: order.append(name)):
            call_command('migrate_locked', stdout=StringIO())
        self.assertEqual(order, [
            'SELECT pg_advisory_lock', 'migrate', 'reencrypt_secrets', 'SELECT pg_advisory_unlock',
        ])

    def test_lock_is_released_when_migrate_fails(self):
        cursor = mock.MagicMock()
        connection = mock.MagicMock(vendor='postgresql')
        connection.cursor.return_value.__enter__.return_value = cursor
        with mock.patch.object(migrate_locked, 'connections', {'default': connection}), \
                mock.patch.object(migrate_locked, 'call_command', side_effect=RuntimeError('boom')):
            with self.assertRaises(RuntimeError):
                call_command('migrate_locked', stdout=StringIO())
        self.assertIn('pg_advisory_unlock', cursor.execute.call_args_list[-1].args[0])

    def test_other_backends_just_migrate(self):
        cursor, migrate = self._run('sqlite')
        self.assertEqual(migrate.call_args_list, [
            mock.call('migrate', interactive=False), mock.call('reencrypt_secrets'),
        ])
        cursor.execute.assert_not_called()

    @override_settings(IMAGI_ROLE='workspace')
    def test_workspace_tier_wipes_accounts_while_the_cutoff_is_set(self):
        with mock.patch.dict('os.environ', {'WIPE_USERS_JOINED_BEFORE': '2026-10-27T17:00:00Z'}):
            _, migrate = self._run('sqlite')
        self.assertEqual(migrate.call_args_list[-1], mock.call(
            'delete_all_users', joined_before='2026-10-27T17:00:00Z', yes=True))

    @override_settings(IMAGI_ROLE='web')
    def test_web_tier_never_wipes(self):
        with mock.patch.dict('os.environ', {'WIPE_USERS_JOINED_BEFORE': '2026-10-27T17:00:00Z'}):
            _, migrate = self._run('sqlite')
        self.assertNotIn('delete_all_users', [c.args[0] for c in migrate.call_args_list])
