"""Rate limits for the unauthenticated credential endpoints.

Sign-in and registration are the only endpoints an anonymous caller can use to
guess a credential, and a successful guess hands back a DRF token that never
expires. Without a limit the only bound on online password guessing is
bandwidth, so both are capped per client IP here.

These key on the IP rather than the account, so a targeted account cannot be
locked out by an attacker hammering it — the failed-attempt counter in
``views`` handles the per-account side, counting only failures.

Note the cache backend: with Django's default in-process ``LocMemCache`` each
gunicorn worker counts separately, so the effective ceiling is the rate times
the worker count. Pointing ``CACHES`` at a shared backend (Redis, Memcached)
makes these limits exact across workers.
"""

from rest_framework.throttling import SimpleRateThrottle


class LoginRateThrottle(SimpleRateThrottle):
    """Per-IP cap on sign-in attempts, applied to anonymous and authenticated alike."""

    scope = 'auth_signin'

    def get_cache_key(self, request, view):
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request),
        }


class RegisterRateThrottle(LoginRateThrottle):
    """Per-IP cap on account creation."""

    scope = 'auth_register'
