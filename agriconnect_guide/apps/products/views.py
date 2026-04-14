# ============================================================
# AgriConnect — Product & Order Views
# apps/products/views.py
# ============================================================

import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Product, Order, Category
from .serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    ProductWriteSerializer,
    OrderCreateSerializer,
    OrderDetailSerializer,
    CategorySerializer,
)
from apps.users.permissions import IsFarmer, IsOwnerOrAdmin
from apps.users.utils import success_response

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════
# PRODUCTS
# ══════════════════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([AllowAny])   # Public — no login needed to browse
def product_list_view(request):
    """
    List all active products with optional search and filter.
    URL: GET /api/products/

    Query params:
        ?search=tomato          → filter by name or location
        ?category=vegetables    → filter by category slug
        ?location=buea          → filter by location keyword
        ?farmer=<uuid>          → filter by farmer ID

    Returns paginated product list.
    """
    products = Product.objects.filter(
        status=Product.STATUS_ACTIVE
    ).select_related('farmer', 'category')   # Avoid N+1 queries

    # ── Search filter ────────────────────────────────────────
    search = request.query_params.get('search', '').strip()
    if search:
        from django.db.models import Q
        products = products.filter(
            Q(name__icontains=search) |
            Q(location__icontains=search) |
            Q(description__icontains=search)
        )

    # ── Category filter ──────────────────────────────────────
    category_slug = request.query_params.get('category', '').strip()
    if category_slug:
        products = products.filter(category__slug=category_slug)

    # ── Location filter ──────────────────────────────────────
    location = request.query_params.get('location', '').strip()
    if location:
        products = products.filter(location__icontains=location)

    # ── Farmer filter ────────────────────────────────────────
    farmer_id = request.query_params.get('farmer', '').strip()
    if farmer_id:
        products = products.filter(farmer__id=farmer_id)

    # ── Simple manual pagination ─────────────────────────────
    # Returns 12 products per page
    # ?page=2 for the next page
    page_size = 12
    try:
        page = max(1, int(request.query_params.get('page', 1)))
    except ValueError:
        page = 1

    start = (page - 1) * page_size
    end   = start + page_size
    total = products.count()

    serializer = ProductListSerializer(
        products[start:end],
        many=True,
        context={'request': request},
    )

    return success_response(data={
        'results':    serializer.data,
        'total':      total,
        'page':       page,
        'page_size':  page_size,
        'has_next':   end < total,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsFarmer])   # Only logged-in farmers
def product_create_view(request):
    """
    Create a new product listing.
    URL: POST /api/products/create/
    Header: Authorization: Token <token>
    Body: multipart/form-data (because it includes an image)
    """
    serializer = ProductWriteSerializer(
        data=request.data,
        context={'request': request},
    )

    if not serializer.is_valid():
        return Response(
            {'success': False, 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    product = serializer.save()
    logger.info(f'Product created: {product.name} by {request.user.phone}')

    return success_response(
        data=ProductDetailSerializer(product, context={'request': request}).data,
        message='Product listed successfully!',
        status_code=status.HTTP_201_CREATED,
    )


@api_view(['GET'])
@permission_classes([AllowAny])   # Public — anyone can view a product
def product_detail_view(request, pk):
    """
    Get full details for one product.
    URL: GET /api/products/<id>/
    """
    try:
        product = Product.objects.select_related(
            'farmer', 'category'
        ).get(pk=pk, status=Product.STATUS_ACTIVE)
    except Product.DoesNotExist:
        return Response(
            {'success': False, 'error': 'Product not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = ProductDetailSerializer(product, context={'request': request})
    return success_response(data=serializer.data)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def product_update_delete_view(request, pk):
    """
    PATCH  — Update a product (farmer who owns it only).
    DELETE — Remove a product (farmer who owns it or admin).
    URL: /api/products/<id>/edit/
    Header: Authorization: Token <token>
    """
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response(
            {'success': False, 'error': 'Product not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Check ownership
    permission = IsOwnerOrAdmin()
    if not permission.has_object_permission(request, None, product):
        return Response(
            {'success': False, 'error': 'You can only edit your own products.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method == 'DELETE':
        # Soft delete — mark as removed instead of actually deleting
        # This preserves order history
        product.status = Product.STATUS_REMOVED
        product.save()
        logger.info(f'Product removed: {product.name} by {request.user.phone}')
        return success_response(message='Product removed successfully.')

    # PATCH
    serializer = ProductWriteSerializer(
        product,
        data=request.data,
        partial=True,
        context={'request': request},
    )
    if not serializer.is_valid():
        return Response(
            {'success': False, 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    updated_product = serializer.save()
    return success_response(
        data=ProductDetailSerializer(updated_product, context={'request': request}).data,
        message='Product updated successfully.',
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsFarmer])
def my_products_view(request):
    """
    Return all products belonging to the logged-in farmer.
    URL: GET /api/products/mine/
    Header: Authorization: Token <token>
    """
    products = Product.objects.filter(
        farmer=request.user
    ).exclude(
        status=Product.STATUS_REMOVED
    ).select_related('category')

    serializer = ProductListSerializer(products, many=True, context={'request': request})
    return success_response(data=serializer.data)


# ══════════════════════════════════════════════════════════════
# CATEGORIES
# ══════════════════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([AllowAny])
def category_list_view(request):
    """
    List all product categories.
    URL: GET /api/products/categories/
    Used to populate filter dropdowns in the frontend.
    """
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return success_response(data=serializer.data)


# ══════════════════════════════════════════════════════════════
# ORDERS
# ══════════════════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def order_create_view(request):
    """
    Buyer places an order for a product.
    URL: POST /api/products/orders/
    Header: Authorization: Token <token>
    Body: { "product": "<uuid>", "quantity": 2, "note": "…" }
    """
    # Only buyers can place orders
    if request.user.role != 'buyer':
        return Response(
            {'success': False, 'error': 'Only buyers can place orders.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = OrderCreateSerializer(
        data=request.data,
        context={'request': request},
    )

    if not serializer.is_valid():
        return Response(
            {'success': False, 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    order = serializer.save()
    logger.info(
        f'Order placed: product={order.product.name} '
        f'buyer={request.user.phone} qty={order.quantity}'
    )

    return success_response(
        data=OrderDetailSerializer(order, context={'request': request}).data,
        message='Order placed! The farmer will contact you soon.',
        status_code=status.HTTP_201_CREATED,
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_orders_view(request):
    """
    Returns orders relevant to the logged-in user.
    - If farmer  → orders FOR their products
    - If buyer   → orders PLACED by them
    URL: GET /api/products/orders/
    """
    if request.user.role == 'farmer':
        orders = Order.objects.filter(
            product__farmer=request.user
        ).select_related('product', 'buyer')
    else:
        orders = Order.objects.filter(
            buyer=request.user
        ).select_related('product', 'buyer')

    serializer = OrderDetailSerializer(orders, many=True, context={'request': request})
    return success_response(data=serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated, IsFarmer])
def order_update_status_view(request, pk):
    """
    Farmer updates order status (confirm, complete, cancel).
    URL: PATCH /api/products/orders/<id>/status/
    Body: { "status": "confirmed" }
    """
    try:
        order = Order.objects.get(pk=pk, product__farmer=request.user)
    except Order.DoesNotExist:
        return Response(
            {'success': False, 'error': 'Order not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    new_status = request.data.get('status', '').strip()
    allowed    = [Order.STATUS_CONFIRMED, Order.STATUS_COMPLETED, Order.STATUS_CANCELLED]

    if new_status not in allowed:
        return Response(
            {'success': False, 'error': f'Status must be one of: {", ".join(allowed)}'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # If cancelled, restore quantity to product
    if new_status == Order.STATUS_CANCELLED and order.status != Order.STATUS_CANCELLED:
        product = order.product
        product.quantity += order.quantity
        if product.status == Product.STATUS_SOLD_OUT:
            product.status = Product.STATUS_ACTIVE
        product.save()

    order.status = new_status
    order.save()

    return success_response(
        data=OrderDetailSerializer(order, context={'request': request}).data,
        message=f'Order status updated to {new_status}.',
    )
