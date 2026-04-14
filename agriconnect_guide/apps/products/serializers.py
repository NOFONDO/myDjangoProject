# ============================================================
# AgriConnect — Products & Orders Serializers
# apps/products/serializers.py
# ============================================================

import bleach
from rest_framework import serializers
from .models import Product, Order, Category
from apps.users.models import CustomUser


def sanitize(value):
    """Strip HTML/JS from any string input."""
    if isinstance(value, str):
        return bleach.clean(value.strip(), tags=[], strip=True)
    return value


# ── Category ─────────────────────────────────────────────────
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Category
        fields = ['id', 'name', 'slug']


# ── Farmer public info (shown on product cards) ──────────────
class FarmerSummarySerializer(serializers.ModelSerializer):
    """
    Only exposes safe, public farmer information.
    Phone number is NOT included here — contact is done through
    the order system to protect farmer privacy.
    """
    class Meta:
        model  = CustomUser
        fields = ['id', 'name', 'location', 'is_verified']


# ── Product List Serializer (used in the grid view) ──────────
class ProductListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer — only fields needed for the product grid.
    Less data = faster page loads on mobile networks.
    """
    farmer   = FarmerSummarySerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model  = Product
        fields = [
            'id', 'name', 'price', 'unit', 'quantity',
            'location', 'category', 'farmer', 'image_url',
            'status', 'created_at',
        ]

    def get_image_url(self, obj):
        """Return the full absolute URL to the image, or None."""
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


# ── Product Detail Serializer (full product page) ────────────
class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Full product information including description and farmer contact.
    """
    farmer    = FarmerSummarySerializer(read_only=True)
    category  = CategorySerializer(read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model  = Product
        fields = [
            'id', 'name', 'description', 'price', 'unit',
            'quantity', 'location', 'category', 'farmer',
            'image_url', 'status', 'harvest_date', 'created_at',
        ]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


# ── Product Create/Update Serializer ─────────────────────────
class ProductWriteSerializer(serializers.ModelSerializer):
    """
    Used when a farmer creates or updates a product.
    Includes all writable fields and validation.
    """
    # category_id sent as a plain integer from the form
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        required=False,
        allow_null=True,
    )

    class Meta:
        model  = Product
        fields = [
            'name', 'description', 'price', 'unit',
            'quantity', 'location', 'category_id', 'image', 'harvest_date',
        ]

    # ── Field-level validation ────────────────────────────────

    def validate_name(self, value):
        value = sanitize(value)
        if len(value) < 3:
            raise serializers.ValidationError('Product name must be at least 3 characters.')
        if len(value) > 200:
            raise serializers.ValidationError('Product name is too long (max 200 chars).')
        return value

    def validate_description(self, value):
        return sanitize(value)

    def validate_location(self, value):
        return sanitize(value)

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('Price must be greater than 0.')
        if value > 9_999_999:
            raise serializers.ValidationError('Price seems too high. Please check.')
        return value

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError('Quantity must be at least 1.')
        return value

    def validate_image(self, image):
        """Validate image type and size."""
        if not image:
            return image

        # Allowed MIME types
        ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp']
        if hasattr(image, 'content_type') and image.content_type not in ALLOWED_TYPES:
            raise serializers.ValidationError(
                'Only JPEG, PNG, and WEBP images are allowed.'
            )

        # Max 5 MB
        if image.size > 5 * 1024 * 1024:
            raise serializers.ValidationError('Image must be smaller than 5 MB.')

        return image

    def create(self, validated_data):
        # Farmer is set from the request, not from user input
        validated_data['farmer'] = self.context['request'].user
        return super().create(validated_data)


# ── Order Serializers ─────────────────────────────────────────
class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Used when a buyer places an order.
    """
    class Meta:
        model  = Order
        fields = ['product', 'quantity', 'note']

    def validate_note(self, value):
        return sanitize(value)

    def validate(self, data):
        product  = data['product']
        quantity = data['quantity']

        # Check the product is still available
        if not product.is_available:
            raise serializers.ValidationError(
                {'product': 'This product is no longer available.'}
            )

        # Check enough stock
        if quantity > product.quantity:
            raise serializers.ValidationError(
                {'quantity': f'Only {product.quantity} {product.unit} available.'}
            )

        # Buyer cannot order their own product (edge case)
        buyer = self.context['request'].user
        if product.farmer == buyer:
            raise serializers.ValidationError(
                {'product': 'You cannot order your own product.'}
            )

        return data

    def create(self, validated_data):
        product = validated_data['product']
        buyer   = self.context['request'].user

        # Lock in the price at the time of the order
        validated_data['buyer']      = buyer
        validated_data['unit_price'] = product.price
        validated_data['total_price'] = product.price * validated_data['quantity']

        # Reduce available quantity
        product.quantity -= validated_data['quantity']
        if product.quantity == 0:
            product.status = Product.STATUS_SOLD_OUT
        product.save()

        return super().create(validated_data)


class OrderDetailSerializer(serializers.ModelSerializer):
    """
    Full order details — used in dashboard and order history.
    """
    product = ProductListSerializer(read_only=True)
    buyer   = FarmerSummarySerializer(read_only=True)

    class Meta:
        model  = Order
        fields = [
            'id', 'product', 'buyer', 'quantity',
            'unit_price', 'total_price', 'status',
            'note', 'created_at',
        ]
        read_only_fields = ['id', 'unit_price', 'total_price', 'created_at']
