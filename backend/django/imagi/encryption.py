"""
Encryption at rest for the third-party credentials users save in Imagi.

Each kind of credential (a project's Stripe keys, its Twilio auth token, its ad
account tokens) has a Fernet key derived from SECRET_KEY and a fixed purpose
string, so one leaked derived key never opens another kind.

Rotating SECRET_KEY would leave every stored value unreadable, so while it is
being rotated (DJANGO_NEW_SECRET_KEY, see settings) settings.OLD_SECRET_KEY
holds the key it replaced: values stored under it still decrypt, new ones
always use the current key, and the reencrypt_secrets command (run on boot by
migrate_locked) moves the old ones over. The old key only ever decrypts here;
it never signs or verifies anything.
"""

import base64
import hashlib

from django.conf import settings


def _derived(secret_key: str, purpose: str):
    from cryptography.fernet import Fernet
    digest = hashlib.sha256((purpose + secret_key).encode()).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def current_fernet(purpose: str):
    """The Fernet for `purpose` under the current SECRET_KEY alone."""
    return _derived(settings.SECRET_KEY, purpose)


def fernet(purpose: str):
    """Encrypts under the current SECRET_KEY; also decrypts the old one's values."""
    from cryptography.fernet import MultiFernet
    keys = [settings.SECRET_KEY]
    old = getattr(settings, 'OLD_SECRET_KEY', '')
    if old and old != settings.SECRET_KEY:
        keys.append(old)
    return MultiFernet([_derived(key, purpose) for key in keys])
