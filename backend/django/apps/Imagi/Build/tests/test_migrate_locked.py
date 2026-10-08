from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.test import SimpleTestCase

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

    def test_postgres_migrates_inside_the_advisory_lock(self):
        order = []
        cursor = mock.MagicMock()
        cursor.execute.side_effect = lambda sql, params: order.append(sql.split('(')[0])
        connection = mock.MagicMock(vendor='postgresql')
        connection.cursor.return_value.__enter__.return_value = cursor
        with mock.patch.object(migrate_locked, 'connections', {'default': connection}), \
                mock.patch.object(migrate_locked, 'call_command',
                                  side_effect=lambda *a, **k: order.append('migrate')):
            call_command('migrate_locked', stdout=StringIO())
        self.assertEqual(order, ['SELECT pg_advisory_lock', 'migrate', 'SELECT pg_advisory_unlock'])

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
        migrate.assert_called_once_with('migrate', interactive=False)
        cursor.execute.assert_not_called()
