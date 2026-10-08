"""
API views for the Sell app.

Owner-facing endpoints are scoped to a project owned by the authenticated
user: /api/v1/sell/projects/<project_id>/...

The storefront endpoints (product list, checkout session, session status)
are public — they're called by the business's own app or by a customer's
browser, not by an Imagi user. The webhook endpoint authenticates requests
with Stripe's signature header instead of a user session.
"""

import datetime
import logging

import stripe
from django.conf import settings as django_settings
from django.db.models import Q, Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.Imagi.ProjectManager.models import Project
from imagi.redirect_urls import UnsafeRedirectError, resolve_redirect_url

from ..models import Customer, Order, Product, SellSettings, Subscription
from ..services.connect_service import ConnectService
from ..services.payment_templates import app_payments_state, install_payments
from ..services.sell_service import (
    SellService,
    SellServiceError,
    default_cancel_url,
    default_success_url,
)
from ..services.stripe_client import construct_webhook_event
from .throttles import StorefrontCheckoutThrottle, StorefrontServerThrottle
from .serializers import (
    CustomerSerializer,
    OrderSerializer,
    ProductSerializer,
    PublicProductSerializer,
    SellSettingsSerializer,
    SubscriptionSerializer,
    customers_with_stats,
)

logger = logging.getLogger(__name__)

RECENT_ORDERS_LIMIT = 5


def paginate(request, queryset, default_limit=50, max_limit=200):
    """Slice a queryset by ?limit=&offset= and return (page, total)."""
    try:
        limit = int(request.query_params.get('limit', default_limit))
    except (TypeError, ValueError):
        limit = default_limit
    limit = max(1, min(limit, max_limit))
    try:
        offset = max(int(request.query_params.get('offset', 0)), 0)
    except (TypeError, ValueError):
        offset = 0
    return queryset[offset:offset + limit], queryset.count()


class ProjectScopedView(APIView):
    """Base view resolving the project from the URL and enforcing ownership."""

    permission_classes = [IsAuthenticated]

    def get_project(self) -> Project:
        try:
            return Project.objects.get(
                id=self.kwargs['project_id'],
                user=self.request.user,
                is_active=True,
            )
        except Project.DoesNotExist:
            raise NotFound('Project not found')

    def get_settings(self, project) -> SellSettings:
        settings_obj, _ = SellSettings.objects.get_or_create(project=project)
        return settings_obj


# -- Settings ------------------------------------------------------------------


class SellSettingsView(ProjectScopedView):
    """Read or update the project's Stripe configuration."""

    def get(self, request, project_id):
        settings_obj = self.get_settings(self.get_project())
        return Response({'settings': SellSettingsSerializer(settings_obj).data})

    def put(self, request, project_id):
        settings_obj = self.get_settings(self.get_project())
        serializer = SellSettingsSerializer(settings_obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'settings': SellSettingsSerializer(settings_obj).data})


class VerifyConnectionView(ProjectScopedView):
    """Test the stored Stripe secret key by fetching the account."""

    def post(self, request, project_id):
        project = self.get_project()
        self.get_settings(project)
        try:
            result = SellService(project).verify()
        except SellServiceError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        settings_obj = SellSettings.objects.get(project=project)
        return Response({
            'verified': True,
            **result,
            'settings': SellSettingsSerializer(settings_obj).data,
        })


# -- Stripe Connect --------------------------------------------------------------


class ConnectStartView(ProjectScopedView):
    """Start (or resume) Stripe's hosted sign-up for the project's account."""

    def post(self, request, project_id):
        project = self.get_project()
        return_path = str(request.data.get('return_path', '') or '')
        try:
            url = ConnectService(project).start_onboarding(return_path)
        except SellServiceError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'url': url})


class ConnectRefreshView(ProjectScopedView):
    """Re-read the connected account's status (after returning from Stripe)."""

    def post(self, request, project_id):
        project = self.get_project()
        try:
            ConnectService(project).refresh()
        except SellServiceError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        settings_obj = SellSettings.objects.get(project=project)
        return Response({'settings': SellSettingsSerializer(settings_obj).data})


class ConnectDisconnectView(ProjectScopedView):
    """Unlink the Stripe account from this project (the account itself stays)."""

    def post(self, request, project_id):
        project = self.get_project()
        ConnectService(project).disconnect()
        settings_obj = SellSettings.objects.get(project=project)
        return Response({'settings': SellSettingsSerializer(settings_obj).data})


class ServerKeyView(ProjectScopedView):
    """
    The key the business's own backend uses for usage reports and plan
    checks. GET reveals it to the owner; POST issues a new one.
    """

    def get(self, request, project_id):
        settings_obj = self.get_settings(self.get_project())
        return Response({'server_key': settings_obj.server_key})

    def post(self, request, project_id):
        settings_obj = self.get_settings(self.get_project())
        key = settings_obj.rotate_server_key()
        settings_obj.save(update_fields=['server_key_encrypted', 'updated_at'])
        return Response({
            'server_key': key,
            'settings': SellSettingsSerializer(settings_obj).data,
        }, status=status.HTTP_201_CREATED)


# -- Overview --------------------------------------------------------------------


def monthly_cents(product) -> int:
    """A fixed plan's price per month (pay-as-you-go has no fixed amount)."""
    if not product:
        return 0
    if product.billing_interval == Product.BILLING_MONTH:
        return product.price_cents
    if product.billing_interval == Product.BILLING_YEAR:
        return round(product.price_cents / 12)
    return 0


class OverviewView(ProjectScopedView):
    """Dashboard stats for the Sell console."""

    def get(self, request, project_id):
        project = self.get_project()
        settings_obj = SellSettings.objects.filter(project=project).first()
        products = project.sell_products.all()
        orders = project.sell_orders.all()
        since = timezone.now() - datetime.timedelta(days=30)
        paid = orders.filter(status__in=list(Order.PAID_STATUSES))
        paid_30d = paid.filter(paid_at__gte=since)
        active_subs = project.sell_subscriptions.filter(
            status__in=list(Subscription.ACTIVE_STATUSES)
        ).select_related('product')

        recent_orders = orders.prefetch_related('items')[:RECENT_ORDERS_LIMIT]
        prices_by_model = {'one_time': 0, 'subscription': 0, 'usage': 0}
        for product in products.filter(is_active=True):
            prices_by_model[product.pricing_model] += 1

        return Response({
            'stats': {
                'configured': bool(settings_obj and settings_obj.is_configured),
                'currency': settings_obj.currency if settings_obj else 'usd',
                'products_total': products.count(),
                'products_active': products.filter(is_active=True).count(),
                'prices_by_model': prices_by_model,
                'customers_total': project.sell_customers.count(),
                'orders_total': orders.count(),
                'orders_pending': orders.filter(status=Order.STATUS_PENDING).count(),
                'orders_paid_30d': paid_30d.count(),
                'revenue_cents_30d': paid_30d.aggregate(
                    total=Sum('amount_total_cents', default=0)
                )['total'],
                'subscriptions_active': active_subs.count(),
                'mrr_cents': sum(monthly_cents(sub.product) for sub in active_subs),
                'usage_units_30d': project.sell_usage_events.filter(
                    created_at__gte=since
                ).aggregate(total=Sum('quantity', default=0))['total'],
            },
            'recent_orders': OrderSerializer(recent_orders, many=True).data,
        })


# -- Payments in the user's app (prebuilt pages) -----------------------------------


class AppPaymentsView(ProjectScopedView):
    """Whether the app has its payment pages, and which."""

    def get(self, request, project_id):
        return Response(app_payments_state(self.get_project()))


class AppPaymentsInstallView(ProjectScopedView):
    """Add (or refresh) the prebuilt payment pages in the user's app."""

    def post(self, request, project_id):
        project = self.get_project()
        try:
            result = install_payments(project)
        except SellServiceError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.exception(f'Failed to add payments to project {project.id}')
            return Response(
                {'error': 'Could not add payments to your app. Try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response(result, status=status.HTTP_201_CREATED)


# -- Subscriptions -----------------------------------------------------------------


class SubscriptionListView(ProjectScopedView):
    """Customers' plans, newest first; ?status=active narrows to live ones."""

    def get(self, request, project_id):
        project = self.get_project()
        subscriptions = project.sell_subscriptions.select_related('product')
        status_filter = request.query_params.get('status', '').strip()
        if status_filter == 'active':
            subscriptions = subscriptions.filter(status__in=list(Subscription.ACTIVE_STATUSES))
        elif status_filter:
            subscriptions = subscriptions.filter(status=status_filter)
        page, total = paginate(request, subscriptions)
        usage = dict(
            project.sell_usage_events.filter(
                subscription__in=[s.id for s in page],
                created_at__gte=timezone.now() - datetime.timedelta(days=30),
            ).values_list('subscription').annotate(total=Sum('quantity'))
        )
        data = SubscriptionSerializer(page, many=True).data
        for row in data:
            row['usage_units_30d'] = usage.get(row['id'], 0)
        return Response({'subscriptions': data, 'total': total})


# -- Products ---------------------------------------------------------------------


class ProductListCreateView(ProjectScopedView):
    """List/search the catalog, or add a product."""

    def get(self, request, project_id):
        project = self.get_project()
        products = project.sell_products.all()

        search = request.query_params.get('search', '').strip()
        if search:
            products = products.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        active = request.query_params.get('active', '').strip()
        if active in ('true', 'false'):
            products = products.filter(is_active=(active == 'true'))

        page, total = paginate(request, products)
        return Response({
            'products': ProductSerializer(page, many=True).data,
            'total': total,
        })

    def post(self, request, project_id):
        project = self.get_project()
        serializer = ProductSerializer(data=request.data, context={'project': project})
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        return Response(
            {'product': ProductSerializer(product).data},
            status=status.HTTP_201_CREATED,
        )


class ProductDetailView(ProjectScopedView):
    """Read, update, or remove a single product."""

    def get_product(self, project, pk) -> Product:
        try:
            return project.sell_products.get(id=pk)
        except Product.DoesNotExist:
            raise NotFound('Product not found')

    def get(self, request, project_id, pk):
        product = self.get_product(self.get_project(), pk)
        return Response({'product': ProductSerializer(product).data})

    def patch(self, request, project_id, pk):
        project = self.get_project()
        product = self.get_product(project, pk)
        serializer = ProductSerializer(
            product, data=request.data, partial=True, context={'project': project}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'product': ProductSerializer(product).data})

    def delete(self, request, project_id, pk):
        product = self.get_product(self.get_project(), pk)
        # Order items keep their name/price snapshot; the FK goes NULL.
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductPaymentLinkView(ProjectScopedView):
    """Create a shareable Stripe Checkout link for one product."""

    def post(self, request, project_id, pk):
        project = self.get_project()
        try:
            product = project.sell_products.get(id=pk, is_active=True)
        except Product.DoesNotExist:
            raise NotFound('Product not found')
        try:
            quantity = int(request.data.get('quantity', 1))
        except (TypeError, ValueError):
            quantity = 1
        try:
            order = SellService(project).create_checkout(
                [{'product_id': product.id, 'quantity': quantity}]
            )
        except SellServiceError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'checkout_url': order.checkout_url,
            'order': OrderSerializer(order).data,
        }, status=status.HTTP_201_CREATED)


# -- Orders -----------------------------------------------------------------------


class OrderListView(ProjectScopedView):
    """List orders, newest first, with optional status filter."""

    def get(self, request, project_id):
        project = self.get_project()
        orders = project.sell_orders.prefetch_related('items')
        status_filter = request.query_params.get('status', '').strip()
        if status_filter:
            orders = orders.filter(status=status_filter)
        page, total = paginate(request, orders)
        return Response({
            'orders': OrderSerializer(page, many=True).data,
            'total': total,
        })


class OrderScopedView(ProjectScopedView):
    def get_order(self, project, pk) -> Order:
        try:
            return project.sell_orders.get(id=pk)
        except Order.DoesNotExist:
            raise NotFound('Order not found')


class OrderDetailView(OrderScopedView):
    def get(self, request, project_id, pk):
        order = self.get_order(self.get_project(), pk)
        return Response({'order': OrderSerializer(order).data})


class OrderFulfillView(OrderScopedView):
    """Mark a paid order as fulfilled."""

    def post(self, request, project_id, pk):
        project = self.get_project()
        order = self.get_order(project, pk)
        try:
            order = SellService(project).mark_fulfilled(order)
        except SellServiceError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'order': OrderSerializer(order).data})


class OrderSyncView(OrderScopedView):
    """Refresh the order from Stripe (fallback when webhooks can't reach us)."""

    def post(self, request, project_id, pk):
        project = self.get_project()
        order = self.get_order(project, pk)
        try:
            updated = SellService(project).sync_order(order)
        except SellServiceError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        order.refresh_from_db()
        return Response({'updated': updated, 'order': OrderSerializer(order).data})


# -- Customers --------------------------------------------------------------------


class CustomerListCreateView(ProjectScopedView):
    """List/search customers, or add one manually."""

    def get(self, request, project_id):
        project = self.get_project()
        customers = customers_with_stats(project)
        search = request.query_params.get('search', '').strip()
        if search:
            customers = customers.filter(
                Q(name__icontains=search) | Q(email__icontains=search)
            )
        page, total = paginate(request, customers)
        return Response({
            'customers': CustomerSerializer(page, many=True).data,
            'total': total,
        })

    def post(self, request, project_id):
        project = self.get_project()
        serializer = CustomerSerializer(data=request.data, context={'project': project})
        serializer.is_valid(raise_exception=True)
        customer = serializer.save()
        return Response(
            {'customer': CustomerSerializer(customer).data},
            status=status.HTTP_201_CREATED,
        )


class CustomerDetailView(ProjectScopedView):
    """Read (with order history), update, or remove a customer."""

    def get_customer(self, project, pk) -> Customer:
        try:
            return customers_with_stats(project).get(id=pk)
        except Customer.DoesNotExist:
            raise NotFound('Customer not found')

    def get(self, request, project_id, pk):
        customer = self.get_customer(self.get_project(), pk)
        orders = customer.orders.prefetch_related('items')
        return Response({
            'customer': CustomerSerializer(customer).data,
            'orders': OrderSerializer(orders, many=True).data,
        })

    def patch(self, request, project_id, pk):
        project = self.get_project()
        customer = self.get_customer(project, pk)
        serializer = CustomerSerializer(
            customer, data=request.data, partial=True, context={'project': project}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'customer': CustomerSerializer(customer).data})

    def delete(self, request, project_id, pk):
        customer = self.get_customer(self.get_project(), pk)
        customer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -- Storefront (public) -----------------------------------------------------------


class PublicView(APIView):
    """
    Base for endpoints called by the business's own app or its customers.
    There's no Imagi user session; the project is resolved by id only.
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    def get_public_project(self, project_id) -> Project:
        try:
            return Project.objects.get(id=project_id, is_active=True)
        except Project.DoesNotExist:
            raise NotFound('Unknown project')


class PublicProductListView(PublicView):
    """Active products for a project — powers a storefront."""

    def get(self, request, project_id):
        project = self.get_public_project(project_id)
        settings_obj = SellSettings.objects.filter(project=project).first()
        products = project.sell_products.filter(is_active=True)
        return Response({
            'currency': settings_obj.currency if settings_obj else 'usd',
            'products': PublicProductSerializer(products, many=True).data,
        })


class PublicCheckoutView(PublicView):
    """
    Start a Stripe Checkout for a cart of the project's products. Returns
    the hosted checkout URL to redirect the customer to. Prices come from
    the catalog, never from the request.
    """

    throttle_classes = [StorefrontCheckoutThrottle]

    def post(self, request, project_id):
        project = self.get_public_project(project_id)
        # This endpoint is unauthenticated and the project id is a sequential
        # integer, so anyone can mint a Checkout session on any merchant's
        # Stripe account. A free-form redirect target would let them choose
        # where the paying customer lands — the merchant's real branded Stripe
        # page handing the customer to an attacker's "receipt" form. Only this
        # app's own origin, a path inside it, the business's published app
        # (its app URL), or, in test mode, a loopback preview is accepted.
        extra_origins = SellService(project).redirect_origins(
            request.data.get('success_url'), request.data.get('cancel_url'),
        )
        try:
            success_url = resolve_redirect_url(
                request.data.get('success_url'),
                default_success_url(project.id),
                extra_origins,
            )
            cancel_url = resolve_redirect_url(
                request.data.get('cancel_url'),
                default_cancel_url(project.id),
                extra_origins,
            )
        except UnsafeRedirectError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            order = SellService(project).create_checkout(
                request.data.get('items'),
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=str(request.data.get('customer_email', '') or '').strip(),
            )
        except SellServiceError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'checkout_url': order.checkout_url,
            'session_id': order.stripe_checkout_session_id,
        }, status=status.HTTP_201_CREATED)


class PublicSessionStatusView(PublicView):
    """
    Status of a checkout by its Stripe session id — polled by the success
    page. Syncs from Stripe while the order is still pending so the page
    works even before webhooks are configured.
    """

    def get(self, request, project_id, session_id):
        project = self.get_public_project(project_id)
        order = project.sell_orders.filter(
            stripe_checkout_session_id=session_id,
        ).first()
        if not order:
            raise NotFound('Unknown checkout session')
        if order.status == Order.STATUS_PENDING:
            try:
                SellService(project).sync_order(order)
                order.refresh_from_db()
            except SellServiceError:
                logger.warning(
                    f'Could not sync checkout session {session_id} for project {project_id}'
                )
        recurring = order.items.filter(
            product__billing_interval__in=[
                Product.BILLING_MONTH, Product.BILLING_YEAR, Product.BILLING_USAGE,
            ]
        ).exists()
        return Response({
            'status': order.status,
            'amount_total_cents': order.amount_total_cents,
            'currency': order.currency,
            'mode': 'subscription' if recurring else 'payment',
        })


# -- Server API (the business's own backend, authenticated by server key) -----------


class ServerAPIView(PublicView):
    """
    Called by the business's backend (apps.payments in the generated app),
    never by a browser. Authenticated with the project's server key.
    """

    throttle_classes = [StorefrontServerThrottle]

    def authorize(self, request, project_id) -> Project:
        project = self.get_public_project(project_id)
        header = request.headers.get('Authorization', '')
        candidate = header[7:].strip() if header.lower().startswith('bearer ') else ''
        config = SellSettings.objects.filter(project=project).first()
        if not config or not config.check_server_key(candidate):
            raise NotAuthenticated('A valid server key is required.')
        return project


class UsageReportView(ServerAPIView):
    """Report pay-as-you-go usage for a customer."""

    def post(self, request, project_id):
        project = self.authorize(request, project_id)
        try:
            event = SellService(project).report_usage(
                request.data.get('customer_email'),
                request.data.get('quantity'),
                idempotency_key=str(request.data.get('idempotency_key', '') or ''),
                product_id=request.data.get('product_id'),
            )
        except SellServiceError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'recorded': True,
            'id': event.id,
            'quantity': event.quantity,
            'product_id': event.product_id,
        }, status=status.HTTP_201_CREATED)


class CustomerPlansView(ServerAPIView):
    """A customer's active plans, so the app can unlock what they paid for."""

    def get(self, request, project_id):
        project = self.authorize(request, project_id)
        email = request.query_params.get('email', '')
        plans = SellService(project).active_subscriptions(email)
        return Response({'subscriptions': [
            {
                'product_id': sub.product_id,
                'name': sub.product_name,
                'type': sub.product.pricing_model if sub.product else 'subscription',
                'status': sub.status,
                'current_period_end': sub.current_period_end,
                'cancel_at_period_end': sub.cancel_at_period_end,
            }
            for sub in plans
        ]})


# -- Stripe webhook -----------------------------------------------------------------


class StripeWebhookView(PublicView):
    """
    Endpoint Stripe calls directly. Authenticity comes from validating the
    Stripe-Signature header with the project's stored signing secret.
    """

    def post(self, request, project_id):
        project = self.get_public_project(project_id)
        config = SellSettings.objects.filter(project=project).first()
        webhook_secret = config.stripe_webhook_secret if config else ''
        if not webhook_secret:
            logger.warning(f'Rejected Stripe webhook for project {project_id}: no signing secret stored')
            return Response(status=status.HTTP_403_FORBIDDEN)

        signature = request.headers.get('Stripe-Signature', '')
        try:
            event = construct_webhook_event(request.body, signature, webhook_secret)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError:
            logger.warning(f'Rejected unsigned Stripe webhook for project {project_id}')
            return Response(status=status.HTTP_403_FORBIDDEN)

        SellService(project).handle_webhook_event(event)
        return Response(status=status.HTTP_200_OK)


class ConnectWebhookView(PublicView):
    """
    The single endpoint for events from every connected account, registered
    once on Imagi's platform account ("Events on Connected accounts").
    Authenticated by STRIPE_CONNECT_WEBHOOK_SECRET; `event.account` says
    which project it's for.
    """

    def post(self, request):
        secret = getattr(django_settings, 'STRIPE_CONNECT_WEBHOOK_SECRET', '')
        if not secret:
            logger.warning('Rejected Connect webhook: STRIPE_CONNECT_WEBHOOK_SECRET is not set')
            return Response(status=status.HTTP_403_FORBIDDEN)
        signature = request.headers.get('Stripe-Signature', '')
        try:
            event = construct_webhook_event(request.body, signature, secret)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError:
            logger.warning('Rejected unsigned Connect webhook')
            return Response(status=status.HTTP_403_FORBIDDEN)

        account_id = event.get('account') or ''
        if not account_id:
            return Response(status=status.HTTP_200_OK)
        config = SellSettings.objects.filter(
            connect_account_id=account_id
        ).select_related('project').first()
        if not config or not config.project.is_active:
            return Response(status=status.HTTP_200_OK)

        if event.get('type') == 'account.updated':
            obj = (event.get('data') or {}).get('object') or {}
            ConnectService(config.project).apply_account(obj)
        else:
            SellService(config.project).handle_webhook_event(event)
        return Response(status=status.HTTP_200_OK)
