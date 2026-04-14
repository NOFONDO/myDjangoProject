# ============================================================
# AgriConnect — Products Admin Configuration
# apps/products/admin.py
# ============================================================

from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Order, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}   # Auto-fill slug from name
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ['name', 'farmer', 'price', 'quantity', 'status', 'location', 'created_at', 'image_preview']
    list_filter   = ['status', 'category', 'created_at']
    search_fields = ['name', 'farmer__name', 'farmer__phone', 'location']
    readonly_fields = ['created_at', 'updated_at', 'image_preview']
    list_editable = ['status']

    def image_preview(self, obj):
        """Show a small thumbnail in the admin list."""
        if obj.image:
            return format_html(
                '<img src="{}" style="height:48px;border-radius:4px;object-fit:cover;" />',
                obj.image.url
            )
        return '—'
    image_preview.short_description = 'Image'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ['id_short', 'product', 'buyer', 'quantity', 'total_price', 'status', 'created_at']
    list_filter   = ['status', 'created_at']
    search_fields = ['product__name', 'buyer__name', 'buyer__phone']
    readonly_fields = ['unit_price', 'total_price', 'created_at']
    list_editable = ['status']

    def id_short(self, obj):
        return str(obj.id)[:8] + '…'
    id_short.short_description = 'Order ID'
