from django.apps import AppConfig
from django.conf import settings
from django.core import checks


@checks.register(checks.Tags.security)
def stripe_webhook_secret_check(app_configs, **kwargs):
    """Surface an unset STRIPE_WEBHOOK_SECRET at deploy time.

    The webhook is the only path that writes Subscription rows, and it is
    unauthenticated by design (Stripe signs it instead). With no signing secret
    the signature is computable by anyone, so the view and the service both
    refuse to run without one — this check reports the same condition from
    `manage.py check` before a deploy discovers it as 503s.

    Deliberately not an ImproperlyConfigured raised from settings: the same
    image runs as three Railway services and only the API one carries the
    Stripe environment, so a hard failure at import would take down services
    that never touch Stripe.
    """
    # Only meaningful where Stripe is actually configured: the same image runs
    # as services that never touch payments, and they should stay quiet.
    if settings.DEBUG or not settings.STRIPE_SECRET_KEY or settings.STRIPE_WEBHOOK_SECRET:
        return []
    return [
        checks.Warning(
            'STRIPE_WEBHOOK_SECRET is not set; the Stripe webhook will reject '
            'every event with 503 and no subscription change will be applied.',
            hint='Set STRIPE_WEBHOOK_SECRET to the signing secret from the Stripe dashboard.',
            id='payments.W001',
        )
    ]


class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.Payments'
