# ============================================================
# AgriConnect — Products & Orders Models
# apps/products/models.py
# ============================================================

import uuid
import os
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from apps.users.models import CustomUser


def product_image_path(instance, filename):
    """
    Build a safe, organised path for uploaded product images.
    Stores as: media/products/<farmer_id>/<uuid>.<ext>
    This prevents directory traversal and filename collisions.
    """
    ext      = os.path.splitext(filename)[1].lower()
    new_name = f'{uuid.uuid4()}{ext}'
    return os.path.join('products', str(instance.farmer.id), new_name)


class Category(models.Model):
    """
    Product categories (Vegetables, Fruits, Grains …).
    Managed by admin — farmers pick from this list.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    A farm product listed by a farmer.
    """

    STATUS_ACTIVE   = 'active'
    STATUS_SOLD_OUT = 'sold_out'
    STATUS_REMOVED  = 'removed'

    STATUS_CHOICES = [
        (STATUS_ACTIVE,   'Active'),
        (STATUS_SOLD_OUT, 'Sold Out'),
        (STATUS_REMOVED,  'Removed'),
    ]

    # UUID primary key — harder to enumerate than integers
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Who listed this product
    farmer = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,      # Delete products if farmer account deleted
        related_name='products',
        limit_choices_to={'role': 'farmer'},   # Only farmers can own products
    )

    # Core fields
    name        = models.CharField(max_length=200)
    description = models.TextField(max_length=2000, blank=True)
    price       = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(1)],   # Price must be at least 1 XAF
    )
    quantity    = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )
    unit        = models.CharField(max_length=50, default='kg')  # kg, basket, bunch…
    location    = models.CharField(max_length=200)
    category    = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='products',
    )

    # Image — stored in media/products/<farmer_id>/<uuid>.jpg
    image = models.ImageField(
        upload_to=product_image_path,
        null=True,
        blank=True,
    )

    # Status
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    harvest_date = models.DateField(null=True, blank=True)

    # Timestamps
    created_at  = models.DateTimeField(default=timezone.now)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} by {self.farmer.name}'

    @property
    def is_available(self):
        return self.status == self.STATUS_ACTIVE and self.quantity > 0


class Order(models.Model):
    """
    A buyer's request to purchase a product.
    """

    STATUS_PENDING   = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING,   'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    product  = models.ForeignKey(Product,    on_delete=models.PROTECT, related_name='orders')
    buyer    = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='orders',
                                 limit_choices_to={'role': 'buyer'})

    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    # Store price at time of order — price may change later
    unit_price   = models.DecimalField(max_digits=10, decimal_places=2)
    total_price  = models.DecimalField(max_digits=10, decimal_places=2)

    status  = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    note    = models.TextField(max_length=500, blank=True)  # Buyer's message to farmer

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{str(self.id)[:8]} — {self.product.name} by {self.buyer.name}'

    def save(self, *args, **kwargs):
        # Auto-calculate total price before saving
        if self.unit_price and self.quantity:
            self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)
