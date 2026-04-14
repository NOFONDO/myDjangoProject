# ============================================================
# AgriConnect — Products URL Patterns
# apps/products/urls.py
#
# All prefixed with /api/products/ (set in config/urls.py)
# ============================================================

from django.urls import path
from . import views

urlpatterns = [

    # ── Product endpoints ────────────────────────────────────

    # GET  /api/products/              → browse all products (public)
    path('', views.product_list_view, name='product-list'),

    # POST /api/products/create/       → farmer lists new product
    path('create/', views.product_create_view, name='product-create'),

    # GET  /api/products/<id>/         → product detail page (public)
    path('<uuid:pk>/', views.product_detail_view, name='product-detail'),

    # PATCH /api/products/<id>/edit/   → farmer edits product
    # DELETE /api/products/<id>/edit/  → farmer removes product
    path('<uuid:pk>/edit/', views.product_update_delete_view, name='product-edit'),

    # GET /api/products/mine/          → farmer sees their own products
    path('mine/', views.my_products_view, name='product-mine'),

    # ── Category endpoints ───────────────────────────────────

    # GET /api/products/categories/    → list all categories (public)
    path('categories/', views.category_list_view, name='category-list'),

    # ── Order endpoints ──────────────────────────────────────

    # POST /api/products/orders/       → buyer places order
    # GET  /api/products/orders/       → view my orders
    path('orders/', views.order_create_view, name='order-create'),
    path('orders/mine/', views.my_orders_view, name='order-mine'),

    # PATCH /api/products/orders/<id>/status/ → farmer updates status
    path('orders/<uuid:pk>/status/', views.order_update_status_view, name='order-status'),
]
