# ============================================================
# AgriConnect — Custom User Model
# apps/users/models.py
#
# WHY a custom user model?
# Django's default User uses a username. We want phone number
# as the login identifier. Always do this BEFORE first migration.
# ============================================================

import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """
    Tells Django how to create users when using our custom model.
    Required when you replace the default User model.
    """

    def create_user(self, phone, password=None, **extra_fields):
        """
        Create a regular user (farmer or buyer).
        Called when someone registers via the API.
        """
        if not phone:
            raise ValueError('Phone number is required.')

        # Normalize phone — strip spaces for consistent storage
        phone = phone.strip().replace(' ', '')

        user = self.model(phone=phone, **extra_fields)

        # hash_password() uses PBKDF2 + SHA256 — never stored as plain text
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        """
        Create an admin user (used by: python manage.py createsuperuser).
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')

        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Our application's user.
    - Farmers can list products and receive orders.
    - Buyers can browse products and place orders.
    """

    # ── Role choices ────────────────────────────────────────
    ROLE_FARMER = 'farmer'
    ROLE_BUYER  = 'buyer'
    ROLE_ADMIN  = 'admin'

    ROLE_CHOICES = [
        (ROLE_FARMER, 'Farmer'),
        (ROLE_BUYER,  'Buyer'),
        (ROLE_ADMIN,  'Admin'),
    ]

    # ── Fields ──────────────────────────────────────────────

    # UUID as primary key — harder to enumerate than 1, 2, 3...
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # Login identifier (replaces username)
    phone = models.CharField(
        max_length=20,
        unique=True,             # No two users can share a phone
        verbose_name='Phone Number',
    )

    # Full name — stored as one field for simplicity
    name = models.CharField(max_length=150, verbose_name='Full Name')

    # Role determines what the user can do
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=ROLE_BUYER,
    )

    # Location — helps buyers find local farmers
    location = models.CharField(max_length=200, blank=True)

    # Standard Django permission fields
    is_active  = models.BooleanField(default=True)    # False = account disabled
    is_staff   = models.BooleanField(default=False)   # Can access /admin
    is_verified = models.BooleanField(default=False)  # Verified farmer (future use)

    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    updated_at  = models.DateTimeField(auto_now=True)

    # ── Tell Django which field is the login ─────────────────
    USERNAME_FIELD  = 'phone'
    REQUIRED_FIELDS = ['name']    # Asked when running createsuperuser

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return f'{self.name} ({self.phone}) — {self.role}'

    # ── Helper properties ────────────────────────────────────
    @property
    def is_farmer(self):
        return self.role == self.ROLE_FARMER

    @property
    def is_buyer(self):
        return self.role == self.ROLE_BUYER
