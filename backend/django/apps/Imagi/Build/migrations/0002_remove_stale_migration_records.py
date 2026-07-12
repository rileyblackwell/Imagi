"""
Remove stale django_migrations rows left behind by the old Agents and
Builder apps, which were merged into Build. The apps no longer exist, so
their migration records are dead weight. Safe to run anywhere: databases
that never had those apps simply delete zero rows.
"""

from django.db import migrations

OLD_APP_LABELS = ('Agents', 'Builder')


def remove_stale_records(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            'DELETE FROM django_migrations WHERE app IN (%s, %s)',
            OLD_APP_LABELS,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('Build', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(remove_stale_records, migrations.RunPython.noop),
    ]
