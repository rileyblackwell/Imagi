"""
API views for the Payments app.

Access is sold as subscription plans with a metered dollar allowance, so this
surface covers subscribing (Checkout), managing the subscription (Billing
Portal), reporting usage against the plan allowance, and the Stripe webhook
that keeps the plan in sync. There is no spendable balance to top up: the
prepaid-credit endpoints were removed along with the balance they drew from.
The history endpoints remain read-only views of past credit purchases.
"""

import stripe
import logging
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings

from ..models import StripeCustomer, Subscription
from ..services.stripe_service import StripeService
from ..services.transaction_service import TransactionService
from ..services.payment_method_service import PaymentMethodService
from ..services.plans import DEFAULT_PLAN_ID, PLANS, list_plans, plan_id_for_lookup_key
from ..services.usage_service import get_usage_status
from .serializers import (
    TransactionSerializer,
    PaymentHistorySerializer,
)

logger = logging.getLogger(__name__)

# Initialize services
stripe_service = StripeService()
transaction_service = TransactionService()
payment_method_service = PaymentMethodService()


class UsageStatusView(APIView):
    """Get the user's plan, rolling usage windows, and the plan registry."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            payload = get_usage_status(request.user)
            # Ship the full registry too so the frontend can render plan options.
            payload['plans'] = list_plans()
            return Response(payload)
        except Exception:
            logger.exception("Error fetching usage status")
            raise


class PaymentHistoryView(generics.ListAPIView):
    """List the user's historical credit purchases."""
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentHistorySerializer

    def get_queryset(self):
        return transaction_service.get_payment_history(self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'payments': serializer.data
        })


class TransactionHistoryView(generics.ListAPIView):
    """List the user's transaction history with optional filtering."""
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        status_filter = self.request.query_params.get('status')
        sort_by = self.request.query_params.get('sort_by', 'created_at')
        sort_order = self.request.query_params.get('sort_order', 'desc')

        result = transaction_service.get_transactions(
            self.request.user,
            status=status_filter,
            sort_by=sort_by,
            sort_order=sort_order
        )

        return result['transactions']

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'transactions': serializer.data,
            'total_count': queryset.count()
        })


class PaymentMethodsView(APIView):
    """Get user's saved payment methods."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get customer ID
            customer_id = payment_method_service.get_stripe_customer_id(request.user)

            if not customer_id:
                return Response([])

            # Get payment methods from Stripe
            payment_methods = stripe_service.list_payment_methods(customer_id)

            return Response(payment_methods)

        except Exception:
            logger.exception("Error fetching payment methods")
            raise


def _ensure_stripe_customer(user):
    """The user's Stripe customer id, creating the customer on first need."""
    customer_id = payment_method_service.get_stripe_customer_id(user)
    if customer_id:
        return customer_id
    customer = stripe_service.create_customer(
        email=user.email,
        name=f"{user.first_name} {user.last_name}".strip() or user.username,
        metadata={'user_id': str(user.id)}
    )
    payment_method_service.set_stripe_customer_id(user, customer.id)
    return customer.id


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def setup_customer(request):
    """Set up a Stripe customer for the user."""
    try:
        # Check if user already has a Stripe customer ID
        customer_id = payment_method_service.get_stripe_customer_id(request.user)

        if customer_id:
            try:
                # Verify customer exists
                customer = stripe_service.get_customer(customer_id)
                return Response({
                    'customer_id': customer.id
                })
            except stripe.error.InvalidRequestError:
                # Customer doesn't exist in Stripe, create new one
                pass

        # Create a new customer
        customer = stripe_service.create_customer(
            email=request.user.email,
            name=f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            metadata={
                'user_id': str(request.user.id)
            }
        )

        # Save customer ID against the user
        payment_method_service.set_stripe_customer_id(request.user, customer.id)

        return Response({
            'customer_id': customer.id
        })

    except Exception:
        logger.exception("Error setting up customer")
        raise


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def attach_payment_method(request):
    """Attach a payment method to the user's Stripe customer."""
    try:
        payment_method_id = request.data.get('payment_method_id')
        if not payment_method_id:
            return Response({
                'error': 'Payment method ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        customer_id = _ensure_stripe_customer(request.user)

        # Attach payment method to customer
        payment_method = stripe_service.attach_payment_method(payment_method_id, customer_id)

        # Store payment method details
        card = payment_method.card
        payment_method_service.create_payment_method(request.user, {
            'payment_method_id': payment_method.id,
            'card_brand': card.brand,
            'last4': card.last4,
            'exp_month': card.exp_month,
            'exp_year': card.exp_year
        })

        return Response({
            'success': True,
            'payment_method': payment_method
        })

    except stripe.error.StripeError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        logger.exception("Error attaching payment method")
        raise


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    """Create a Stripe Checkout Session for a subscription plan.

    Subscriptions are the only thing that can be bought: a plan grants a
    metered usage allowance, so there is no one-time purchase mode.
    """
    try:
        lookup_key = request.data.get('lookup_key')
        success_url = request.data.get('success_url', f"{settings.FRONTEND_URL}/payments/success")
        cancel_url = request.data.get('cancel_url', f"{settings.FRONTEND_URL}/payments/cancel")

        if not lookup_key:
            return Response({
                'error': 'lookup_key is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Refuse lookup_keys that don't name a plan we meter, rather than
        # selling a subscription the webhook would later fail to resolve.
        if plan_id_for_lookup_key(lookup_key) is None:
            return Response({
                'error': f'Unknown plan for lookup_key: {lookup_key}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Look up the price by lookup_key (Stripe's recommended pattern)
        prices = stripe.Price.list(
            lookup_keys=[lookup_key],
            expand=['data.product'],
        )

        if not prices.data:
            return Response({
                'error': f'No price found for lookup_key: {lookup_key}'
            }, status=status.HTTP_404_NOT_FOUND)

        line_items = [{'price': prices.data[0].id, 'quantity': 1}]
        metadata = {
            'user_id': str(request.user.id),
            'lookup_key': lookup_key,
        }

        # Subscription mode requires a customer
        customer_id = _ensure_stripe_customer(request.user)

        # Append session_id to success URL per Stripe pattern
        success_url_with_session = f"{success_url}?success=true&session_id={{CHECKOUT_SESSION_ID}}"

        checkout_session = stripe_service.create_checkout_session(
            line_items=line_items,
            metadata=metadata,
            success_url=success_url_with_session,
            cancel_url=cancel_url,
            mode='subscription',
            customer=customer_id,
        )

        return Response({
            'session_id': checkout_session.id,
            'checkout_url': checkout_session.url
        })

    except Exception:
        logger.exception("Error creating checkout session")
        raise


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_portal_session(request):
    """Create a Stripe Billing Portal session for subscription management."""
    try:
        customer_id = payment_method_service.get_stripe_customer_id(request.user)
        if not customer_id:
            return Response({
                'error': 'No Stripe customer found. Please subscribe to a plan first.'
            }, status=status.HTTP_400_BAD_REQUEST)

        return_url = request.data.get('return_url', f"{settings.FRONTEND_URL}/payments/pricing")

        portal_session = stripe_service.create_portal_session(customer_id, return_url)
        return Response({
            'url': portal_session.url
        })

    except Exception:
        logger.exception("Error creating portal session")
        raise


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_session_status(request):
    """Get the status of a Stripe Checkout Session.

    Purely informational for the success page — the plan itself is granted by
    the subscription webhook, never by this call.
    """
    try:
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response({
                'error': 'Session ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve session from Stripe
        session = stripe_service.get_session_status(session_id)

        # Enforce object-level ownership: the session must belong to the
        # caller. session_id is exposed in the success-page URL, so without
        # this any authenticated user holding another user's id could read
        # that user's checkout.
        if session.metadata.get('user_id') != str(request.user.id):
            return Response({
                'error': 'Session not found'
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'status': 'complete' if session.payment_status == 'paid' else 'pending',
            'payment_status': session.payment_status,
            'mode': session.mode,
        })

    except stripe.error.StripeError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        logger.exception("Error checking session status")
        raise


@api_view(['POST'])
@permission_classes([AllowAny])
def webhook(request):
    """Handle Stripe webhooks.

    Authenticated by Stripe's signature (verify_webhook_event) rather than a
    logged-in session, so it must bypass the DRF default IsAuthenticated —
    otherwise Stripe's unauthenticated POST is rejected and the webhook never
    runs, which is the only path that grants and revokes plans.
    """
    try:
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

        try:
            event = stripe_service.verify_webhook_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            logger.error("Invalid webhook payload")
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid webhook signature")
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if event.type in (
            'customer.subscription.created',
            'customer.subscription.updated',
            'customer.subscription.deleted',
        ):
            handle_subscription_event(event.type, event.data.object)

        # Return success response
        return Response({'status': 'success'})

    except Exception:
        logger.exception("Webhook error")
        raise


def _resolve_subscription_plan_id(subscription):
    """Map a Stripe subscription to a plan id, or None when unrecognized.

    The price lookup_key is the canonical mapping (checkout sessions are
    created by lookup_key, which plan_id_for_lookup_key resolves to a plan
    id); metadata['plan'] is the manual fallback.
    """
    items = (subscription.get('items') or {}).get('data') or []
    for item in items:
        lookup_key = (item.get('price') or {}).get('lookup_key')
        plan_id = plan_id_for_lookup_key(lookup_key)
        if plan_id:
            return plan_id
    plan = (subscription.get('metadata') or {}).get('plan')
    if plan in PLANS:
        return plan
    return None


def handle_subscription_event(event_type, subscription):
    """Sync a user's Subscription row from a Stripe subscription event.

    Only ever called from the signature-verified webhook path. The user is
    resolved through StripeCustomer.stripe_customer_id — the single store of
    the Stripe customer id.

    A customer can have several Stripe subscriptions at once (the upgrade
    checkout creates a new one before the old one is cancelled), and Stripe
    does not guarantee event ordering — so events for a subscription other
    than the stored one must never clobber the active plan. Entitlement also
    follows the subscription's standing: a subscription that is not
    active/trialing never grants (or re-affirms) a paid plan.
    """
    try:
        customer_id = subscription.get('customer')
        stripe_customer = (
            StripeCustomer.objects.filter(stripe_customer_id=customer_id).first()
            if customer_id else None
        )
        if stripe_customer is None:
            logger.warning(
                f"Subscription event {event_type} for unknown Stripe customer {customer_id}"
            )
            return
        user = stripe_customer.user

        event_sub_id = subscription.get('id') or ''
        stored = Subscription.objects.filter(user=user).first()
        stored_id = stored.stripe_subscription_id if stored else ''
        # An empty stored id matches anything (backward compatibility with
        # rows written before the id was tracked); so does an event without
        # an id (defensive — real Stripe events always carry one).
        is_stored_subscription = (
            not stored_id or not event_sub_id or stored_id == event_sub_id
        )
        # 'active'/'trialing' are the only statuses in good standing; absent
        # status (never sent by Stripe) is treated as healthy, defensively.
        sub_status = subscription.get('status')
        in_good_standing = sub_status in ('active', 'trialing') or sub_status is None

        if event_type == 'customer.subscription.deleted':
            # Only the stored subscription may downgrade the plan: deleting
            # an old/secondary subscription (e.g. the one an upgrade checkout
            # replaced) must not strip the plan the user is paying for.
            if not is_stored_subscription:
                logger.info(
                    f"Ignoring deleted event for subscription {event_sub_id} "
                    f"(user {user.id} is on {stored_id})"
                )
                return
            Subscription.objects.update_or_create(
                user=user,
                defaults={'plan': DEFAULT_PLAN_ID, 'stripe_subscription_id': ''},
            )
            logger.info(f"Subscription ended for user {user.id}; downgraded to {DEFAULT_PLAN_ID}")
            return

        # created/updated. A different subscription than the stored one takes
        # over only when it is newly created and in good standing (the
        # upgrade-checkout path); stale updates to a replaced subscription
        # are ignored.
        if not is_stored_subscription and not (
            event_type == 'customer.subscription.created' and in_good_standing
        ):
            logger.info(
                f"Ignoring {event_type} for subscription {event_sub_id} "
                f"(user {user.id} is on {stored_id})"
            )
            return

        if not in_good_standing:
            if sub_status == 'past_due':
                # Stripe is still retrying the charge; don't yank entitlement
                # mid-dunning.
                logger.info(
                    f"Subscription {event_sub_id} past_due for user {user.id}; "
                    "leaving plan unchanged during retries"
                )
                return
            # incomplete / incomplete_expired / unpaid / canceled / paused:
            # never keep a paid allowance for a subscription that isn't paying.
            Subscription.objects.update_or_create(
                user=user,
                defaults={
                    'plan': DEFAULT_PLAN_ID,
                    'stripe_subscription_id': event_sub_id,
                },
            )
            logger.info(
                f"Subscription {event_sub_id} is {sub_status} for user {user.id}; "
                f"downgraded to {DEFAULT_PLAN_ID}"
            )
            return

        plan_id = _resolve_subscription_plan_id(subscription)
        if plan_id is None:
            # Unknown price/metadata: leave the stored plan unchanged rather
            # than guessing a downgrade or upgrade.
            logger.warning(
                f"Could not resolve plan for subscription {subscription.get('id')} "
                f"(user {user.id}); leaving plan unchanged"
            )
            return

        Subscription.objects.update_or_create(
            user=user,
            defaults={
                'plan': plan_id,
                'stripe_subscription_id': event_sub_id,
            },
        )
        logger.info(f"Subscription {event_type}: user {user.id} on plan {plan_id}")

    except Exception as e:
        logger.error(f"Error handling subscription event {event_type}: {str(e)}")
