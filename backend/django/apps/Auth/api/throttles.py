"""Rate limits for the unauthenticated credential endpoints.

Sign-in and registration are the only endpoints an anonymous caller can use to
guess a credential, and a successful guess hands back a DRF token that never
expires. Without a limit the only bound on online password guessing is
bandwidth, so both are capped per client IP here.

These key on the IP rather than the account, so a targeted account cannot be
locked out by an attacker hammering it — the failed-attempt counter in
``views`` handles the per-account side, counting only failures.

**Getting the client IP right behind a proxy.** DRF's own ``get_ident`` keys on
the whole ``X-Forwarded-For`` header unless ``NUM_PROXIES`` is pinned to the
exact number of proxies in front of the app. In a deployment like Imagi's —
the platform edge, then the frontend nginx, then Django — that chain varies in
length and in the addresses it carries, so keying on the raw header gives a
different bucket almost every request and the limit silently never fires (it
did not, in production, until this was fixed). Rather than pin a fragile hop
count, :func:`client_ip` derives the real client address from the chain in a
way that does not depend on how many proxies there are and cannot be moved by a
caller-supplied header.

Note the cache backend: with Django's default in-process ``LocMemCache`` each
gunicorn worker counts separately, so the effective ceiling is the rate times
the worker count. Pointing ``CACHES`` at a shared backend (Redis, Memcached, or
the file-based cache Imagi uses) makes these limits exact across workers.

Each throttle carries a default rate, used when settings name none for its
scope. Settings still win, but a project that forgets to configure them keeps
its limits instead of failing every sign-in with ImproperlyConfigured — this
module also ships, unchanged, as the prebuilt auth of every generated project.
"""

import ipaddress

from rest_framework.throttling import SimpleRateThrottle


def client_ip(request) -> str:
    """The requester's real IP, resistant to ``X-Forwarded-For`` spoofing.

    Each proxy in a chain appends the address it received the connection from
    to the right of ``X-Forwarded-For``, so the header reads left-to-right as
    ``<client>, <edge>, <frontend>`` and every hop after the client is on the
    platform's private network. A caller can prepend anything they like to the
    left of the header, but they cannot change what the edge appends, so the
    real client is the right-most *public* address in the chain. Scanning from
    the right for the first public address therefore returns the real client
    and ignores injected values, without needing to know how many proxies are
    in front of the app.

    Falls back to ``REMOTE_ADDR`` (the connecting peer, which a caller cannot
    forge) when there is no forwarded chain — a direct connection — or when the
    chain holds only private addresses, as in local development.
    """
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '') or ''
    hops = [part.strip() for part in forwarded.split(',') if part.strip()]
    for raw in reversed(hops):
        try:
            address = ipaddress.ip_address(raw.split('%', 1)[0])
        except ValueError:
            continue
        if address.is_global:
            return str(address)
    remote_addr = (request.META.get('REMOTE_ADDR', '') or '').strip()
    if remote_addr:
        return remote_addr
    return hops[0] if hops else ''


class ClientIPRateThrottle(SimpleRateThrottle):
    """A per-IP throttle that keys on :func:`client_ip`.

    Overriding ``get_cache_key`` (rather than relying on DRF's proxy-count
    heuristic) is what makes the limit actually accumulate for one client
    behind the proxy chain.
    """

    def get_rate(self):
        return self.THROTTLE_RATES.get(self.scope, self.default_rate)

    def get_cache_key(self, request, view):
        return self.cache_format % {
            'scope': self.scope,
            'ident': client_ip(request) or 'unknown',
        }


class LoginRateThrottle(ClientIPRateThrottle):
    """Per-IP cap on sign-in attempts, applied to anonymous and authenticated alike."""

    scope = 'auth_signin'
    default_rate = '10/min'


class RegisterRateThrottle(ClientIPRateThrottle):
    """Per-IP cap on account creation."""

    scope = 'auth_register'
    default_rate = '20/hour'


class GlobalRegisterRateThrottle(SimpleRateThrottle):
    """A site-wide ceiling on new accounts, on top of the per-IP cap.

    The per-IP limit bounds one source; this bounds the whole site at once, so
    a run spread across many IPs still cannot create accounts faster than the
    site as a whole permits. It is deliberately generous — a brake on mass
    abuse, not on an ordinary burst of genuine sign-ups — and is meant to be
    raised through ``DEFAULT_THROTTLE_RATES['auth_register_global']`` as real
    traffic grows, since once it trips it refuses *every* registration until
    the window rolls. Keyed on a constant so all registrations share one
    window.
    """

    scope = 'auth_register_global'
    default_rate = '120/hour'

    def get_rate(self):
        return self.THROTTLE_RATES.get(self.scope, self.default_rate)

    def get_cache_key(self, request, view):
        return self.cache_format % {'scope': self.scope, 'ident': 'all'}
