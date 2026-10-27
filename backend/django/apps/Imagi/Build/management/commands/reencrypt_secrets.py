"""
Move users' stored credentials from the old SECRET_KEY to the current one.

Rotating the secret key changes the key every saved Stripe key, Twilio token
and ad account token is encrypted with (see imagi.encryption). While
DJANGO_NEW_SECRET_KEY is set, the replaced key is settings.OLD_SECRET_KEY, and
this command re-encrypts each value still under it. migrate_locked runs it on
every boot, so no one has to reach a shell on Railway; outside a rotation it
does nothing, and a second run finds nothing to move.

A value neither key opens is left as it is and counted: it was already
unreadable, and the app treats it as unset so its owner can enter it again.

Usage:
    python manage.py reencrypt_secrets
"""

import logging

from cryptography.fernet import InvalidToken
from django.conf import settings
from django.core.management.base import BaseCommand

from apps.Imagi.Marketing import models as marketing
from apps.Imagi.Sell import models as sell
from imagi import encryption

logger = logging.getLogger(__name__)

# (model, encrypted fields, purpose string of the key they are stored under)
ENCRYPTED_FIELDS = (
    (sell.SellSettings,
     ('stripe_secret_key_encrypted', 'stripe_webhook_secret_encrypted', 'server_key_encrypted'),
     sell.ENCRYPTION_PURPOSE),
    (marketing.MarketingSettings, ('twilio_auth_token_encrypted',), marketing.ENCRYPTION_PURPOSE),
    (marketing.AdConnection, ('credentials_encrypted',), marketing.ENCRYPTION_PURPOSE),
)


def reencrypt_all():
    """Re-encrypt every value stored under the old key. Returns (moved, unreadable)."""
    moved = unreadable = 0
    for model, fields, purpose in ENCRYPTED_FIELDS:
        current = encryption.current_fernet(purpose)
        rotating = encryption.fernet(purpose)
        for row in model.objects.only('pk', *fields).iterator():
            changed = []
            for field in fields:
                token = getattr(row, field)
                if not token:
                    continue
                try:
                    current.decrypt(token.encode())
                    continue
                except InvalidToken:
                    pass
                try:
                    setattr(row, field, rotating.rotate(token.encode()).decode())
                    changed.append(field)
                except InvalidToken:
                    unreadable += 1
            if changed:
                # .update() rather than save(): leaves updated_at alone and
                # can't overwrite a field someone changed meanwhile.
                model.objects.filter(pk=row.pk).update(
                    **{field: getattr(row, field) for field in changed}
                )
                moved += len(changed)
    return moved, unreadable


class Command(BaseCommand):
    help = 'Re-encrypt stored credentials from the replaced secret key to the current one.'

    def handle(self, *args, **options):
        if not settings.OLD_SECRET_KEY or settings.OLD_SECRET_KEY == settings.SECRET_KEY:
            return
        # Runs on boot: a failure here must not keep the server from starting,
        # since the old key still decrypts everything until this succeeds.
        try:
            moved, unreadable = reencrypt_all()
        except Exception:
            logger.exception('reencrypt_secrets failed; stored credentials stay on the old key')
            self.stderr.write('reencrypt_secrets failed; see the log. Values stay readable with the old key.')
            return
        self.stdout.write(
            f'reencrypt_secrets: moved {moved} stored credential(s) to the new SECRET_KEY; '
            f'{unreadable} unreadable under either key. '
            'Once both tiers have deployed, set DJANGO_SECRET_KEY to the new key '
            'and DJANGO_NEW_SECRET_KEY to empty.'
        )
