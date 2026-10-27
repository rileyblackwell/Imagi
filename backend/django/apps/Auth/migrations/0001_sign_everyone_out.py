"""
Sign every user out, once.

Railway reported on 2026-10-21 that customers' environment variables may have
been read, which includes this database's password. Sign-in tokens are stored
in the database as they are, so anyone who read it could act as any user. This
deletes every token and session; each user signs in again and gets a new one.
"""

from django.db import migrations


def sign_everyone_out(apps, schema_editor):
    apps.get_model('authtoken', 'Token').objects.all().delete()
    apps.get_model('sessions', 'Session').objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('authtoken', '0003_tokenproxy'),
        ('sessions', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(sign_everyone_out, migrations.RunPython.noop),
    ]
