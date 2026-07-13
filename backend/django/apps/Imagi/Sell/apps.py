from django.apps import AppConfig


def _cors_allow_storefront(sender, request, **kwargs):
    """
    Let any origin call the public storefront endpoints. The prebuilt
    payment pages installed into users' generated apps run on their own
    domains (or local previews), so the browser needs CORS here. These
    endpoints are unauthenticated by design: prices come from the catalog
    and payment happens on Stripe's hosted page.
    """
    return request.path.startswith('/api/v1/sell/storefront/')


class SellConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.Imagi.Sell'

    def ready(self):
        from corsheaders.signals import check_request_enabled
        check_request_enabled.connect(_cors_allow_storefront)
