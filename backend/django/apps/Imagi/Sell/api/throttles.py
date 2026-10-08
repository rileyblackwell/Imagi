"""Rate limit for the public storefront endpoints.

PublicCheckoutView is unauthenticated and resolves the project by a sequential
integer id, so without a limit anyone can mint unbounded Order rows and
outbound Stripe API calls signed with the merchant's own secret key.
"""

from rest_framework.throttling import SimpleRateThrottle


class StorefrontCheckoutThrottle(SimpleRateThrottle):
    """Per-IP cap on public checkout creation."""

    scope = 'storefront_checkout'

    def get_cache_key(self, request, view):
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request),
        }


class StorefrontServerThrottle(SimpleRateThrottle):
    """Per-project cap on server-key calls (usage reports, plan checks)."""

    scope = 'storefront_server'

    def get_cache_key(self, request, view):
        return self.cache_format % {
            'scope': self.scope,
            'ident': view.kwargs.get('project_id', self.get_ident(request)),
        }
