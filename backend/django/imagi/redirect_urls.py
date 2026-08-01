"""Allowlist for caller-supplied redirect targets.

Stripe Checkout takes the URL the customer lands on after paying or cancelling.
Those URLs arrive in request bodies, and a Stripe-hosted page carrying real
merchant branding that redirects to an attacker's site is a uniquely credible
phishing chain — so no caller-supplied absolute URL is passed through without
its origin being on this allowlist.

Callers that just want a different landing page inside the app pass a relative
path instead, which is resolved against FRONTEND_URL and cannot leave it.
"""

from urllib.parse import urlsplit

from django.conf import settings


class UnsafeRedirectError(ValueError):
    """A caller-supplied redirect URL pointed somewhere not allowlisted."""


def _origin(url):
    """``scheme://host[:port]`` for an absolute http(s) URL, else None."""
    parts = urlsplit(url or '')
    if parts.scheme not in ('http', 'https') or not parts.netloc:
        return None
    return f"{parts.scheme}://{parts.netloc}"


def allowed_origins(extra=()):
    """Origins a redirect may point at: the app's own, plus any caller extras."""
    origins = set()
    for candidate in (settings.FRONTEND_URL, *extra):
        origin = _origin(candidate)
        if origin:
            origins.add(origin)
    return origins


def resolve_redirect_url(value, default, extra_origins=()):
    """Resolve one caller-supplied redirect target to a safe absolute URL.

    ``value`` may be empty (use ``default``), a relative path beginning with a
    single ``/`` (resolved against FRONTEND_URL), or an absolute http(s) URL
    whose origin is allowlisted. Anything else raises UnsafeRedirectError.
    """
    value = (value or '').strip()
    if not value:
        return default

    # A protocol-relative URL ("//evil.example") is absolute to a browser but
    # has no scheme, so it must not be mistaken for a path.
    if value.startswith('/') and not value.startswith('//'):
        return f"{settings.FRONTEND_URL.rstrip('/')}{value}"

    origin = _origin(value)
    if origin is None:
        raise UnsafeRedirectError(
            'Redirect URL must be an absolute http(s) URL or a path beginning with "/".'
        )
    if origin not in allowed_origins(extra_origins):
        raise UnsafeRedirectError(f'Redirect URL origin {origin} is not allowed.')
    return value
