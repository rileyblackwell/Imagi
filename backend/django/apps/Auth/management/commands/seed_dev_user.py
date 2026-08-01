"""Create the throwaway local login used to drive the app in a preview browser.

Agents working in a preview browser need to get past /auth/signin to see
anything behind authentication, and the dev database is gitignored — so a fresh
clone or a reset DB has no account to log in with. This recreates a known one on
demand, so credentials never have to be typed into a registration form by hand.

The account this normally seeds is `imagi-dev`, whose password lives outside the
repo in `~/.config/imagi/test-credentials.env` (see CLAUDE.md). Source that file
and pass --password "$IMAGI_DEV_PASSWORD" to match it. The built-in defaults below
are a public, worthless fallback for a machine that has no such file yet.

Local only, and enforced rather than merely documented:
  - DEBUG must be on. This is the check that gates production, which runs with
    DEBUG=False.
  - The default database must be SQLite. Setting DATABASE_URL is what switches
    imagi/settings.py to Postgres, so a non-SQLite engine means we are pointed
    at a real database and must refuse.
"""

import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from rest_framework.authtoken.models import Token

# Fallback only; the seeded account is normally imagi-dev, from the credentials
# file above.
DEV_USERNAME = 'devuser'
DEV_EMAIL = 'devuser@localhost.invalid'  # .invalid is reserved; can never be a real mailbox
DEV_PASSWORD = 'imagi-local-dev-only'


class Command(BaseCommand):
    help = 'Create or reset the local-only dev login used for preview-browser sign-in.'

    def add_arguments(self, parser):
        parser.add_argument('--username', default=DEV_USERNAME)
        parser.add_argument('--email', default=DEV_EMAIL)
        parser.add_argument('--password', default=DEV_PASSWORD)
        parser.add_argument(
            '--print-token',
            action='store_true',
            help=(
                "Print the account's DRF token as JSON instead of the usual summary. "
                'Lets a preview-browser agent authenticate by seeding localStorage '
                'directly, so no password is ever typed into the sign-in form.'
            ),
        )
        parser.add_argument(
            '--no-reset',
            action='store_true',
            help=(
                'Leave an existing account\'s password and email alone; only ensure it '
                'has a token. Without this, --username imagi-dev would overwrite the '
                'credentials documented in ~/.config/imagi/test-credentials.env with '
                'the fallback defaults. Fails if the account does not exist yet.'
            ),
        )

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError(
                'Refusing to run with DEBUG=False. This command seeds a login with a '
                'publicly documented password and is for local development only.'
            )
        engine = settings.DATABASES['default']['ENGINE']
        if not engine.endswith('sqlite3'):
            raise CommandError(
                f'Refusing to run against {engine}. Setting DATABASE_URL points this '
                'at a real database; the dev login belongs only in the local SQLite DB.'
            )

        username = options['username']
        User = get_user_model()

        if options['no_reset']:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise CommandError(
                    f"No account '{username}' to read a token from. Drop --no-reset to "
                    'create it, passing --password to match your credentials file.'
                )
            token, _ = Token.objects.get_or_create(user=user)
            created = False
        else:
            with transaction.atomic():
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={'email': options['email']},
                )
                # Always reset, so a half-remembered password from an earlier run
                # can't leave the documented credentials wrong.
                user.email = options['email']
                user.set_password(options['password'])
                user.save()
                token, _ = Token.objects.get_or_create(user=user)

        if options['print_token']:
            # Same shape the login endpoint returns, so the caller can drop it
            # straight into the frontend's `token` / `user` localStorage keys.
            from apps.Auth.api.serializers import UserSerializer

            self.stdout.write(json.dumps({
                'token': token.key,
                'user': UserSerializer(user).data,
            }))
            return

        self.stdout.write(self.style.SUCCESS(
            f"{'Created' if created else 'Reset'} dev login '{username}' "
            f"— sign in at /auth/signin with this username, not the email."
        ))
