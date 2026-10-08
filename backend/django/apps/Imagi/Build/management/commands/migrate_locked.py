"""
Apply migrations under a database-wide lock, so every tier can run it on boot.

Production runs one image as two Railway services (see settings.IMAGI_ROLE)
that redeploy from the same push, with nothing ordering them. When only the
web tier migrated, the workspace tier could come up first on new code against
the old schema and fail every query touching a new column until the web tier
caught up — on the deploy that added AgentCheckIn.details the threads list
returned 500s for about ninety seconds. The workspace tier keeps its projects
on a volume, so Railway stops its old container before starting the new one;
waiting for the web tier would only swap those 500s for downtime.

So both tiers migrate, and whichever boots first applies the changes. On
PostgreSQL a session advisory lock serializes them: the second tier blocks
until the first finishes, then finds nothing left to apply. Other backends
(SQLite in dev and tests) have one process and just migrate.

Usage:
    python manage.py migrate_locked
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connections, DEFAULT_DB_ALIAS

# Arbitrary, fixed key shared by every tier ("imagi" in ASCII).
MIGRATE_LOCK_KEY = 0x696D616769


class Command(BaseCommand):
    help = "Run migrate while holding a lock that other tiers' migrate_locked waits on."

    def handle(self, *args, **options):
        connection = connections[DEFAULT_DB_ALIAS]
        if connection.vendor != 'postgresql':
            call_command('migrate', interactive=False)
            return

        with connection.cursor() as cursor:
            self.stdout.write('Waiting for the migration lock...')
            cursor.execute('SELECT pg_advisory_lock(%s)', [MIGRATE_LOCK_KEY])
            try:
                call_command('migrate', interactive=False)
            finally:
                cursor.execute('SELECT pg_advisory_unlock(%s)', [MIGRATE_LOCK_KEY])
