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
from django.db.models import Q, Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.Products.Imagi.ProjectManager.models import Project

from ..models import Customer, Order, Product, SellSettings
from ..services.sell_service import SellService, SellServiceError
from ..services.stripe_client import construct_webhook_event
from .serializers import (
    CustomerSerializer,
    OrderSerializer,
    ProductSerializer,
    PublicProductSerializer,
    SellSettingsSerializer,
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


# -- Overview --------------------------------------------------------------------


class OverviewView(ProjectScopedView):
    """Dashboard stats for the sell workspace."""

    def get(self, request, project_id):
        project = self.get_project()
        settings_obj = SellSettings.objects.filter(project=project).first()
        products = project.sell_products.all()
        orders = project.sell_orders.all()
        since = timezone.now() - datetime.timedelta(days=30)
        paid = orders.filter(status__in=list(Order.PAID_STATUSES))
        paid_30d = paid.filter(paid_at__gte=since)

        recent_orders = orders.prefetch_related('items')[:RECENT_ORDERS_LIMIT]

        return Response({
            'stats': {
                'configured': bool(settings_obj and settings_obj.is_configured),
                'currency': settings_obj.currency if settings_obj else 'usd',
                'products_total': products.count(),
                'products_active': products.filter(is_active=True).count(),
                'customers_total': project.sell_customers.count(),
                'orders_total': orders.count(),
                'orders_pending': orders.filter(status=Order.STATUS_PENDING).count(),
                'orders_paid_30d': paid_30d.count(),
                'revenue_cents_30d': paid_30d.aggregate(
                    total=Sum('amount_total_cents', default=0)
                )['total'],
            },
            'recent_orders': OrderSerializer(recent_orders, many=True).data,
        })


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

    def post(self, request, project_id):
        project = self.get_public_project(project_id)
        success_url = str(request.data.get('success_url', '') or '')
        cancel_url = str(request.data.get('cancel_url', '') or '')
        for url in (success_url, cancel_url):
            if url and not url.startswith(('http://', 'https://')):
                return Response(
                    {'error': 'success_url and cancel_url must be absolute http(s) URLs.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
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
        return Response({
            'status': order.status,
            'amount_total_cents': order.amount_total_cents,
            'currency': order.currency,
        })


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
