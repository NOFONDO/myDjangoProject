# ============================================================
# AgriConnect — User Serializers
# apps/users/serializers.py
#
# Serializers do two jobs:
#   1. Validate incoming data (did the user send what we need?)
#   2. Convert Python objects to JSON (for API responses)
# ============================================================

import bleach
from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import CustomUser


def sanitize(value):
    """
    Strip any HTML/JS tags from user input.
    Prevents stored XSS attacks.
    Example: "<script>alert(1)</script>" → "alert(1)"
    """
    if isinstance(value, str):
        return bleach.clean(value.strip(), tags=[], strip=True)
    return value


class RegisterSerializer(serializers.ModelSerializer):
    """
    Validates and processes new user registration.
    POST /api/auth/register/
    """

    # write_only=True means password is accepted but NEVER returned in responses
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
        error_messages={
            'min_length': 'Password must be at least 8 characters.',
        }
    )

    # Confirm password field — not stored, just used for validation
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
    )

    class Meta:
        model  = CustomUser
        fields = ['name', 'phone', 'password', 'password_confirm', 'role', 'location']

    # ── Field-level validation ───────────────────────────────

    def validate_name(self, value):
        """Name must be at least 2 characters and contain only safe characters."""
        value = sanitize(value)
        if len(value) < 2:
            raise serializers.ValidationError('Name must be at least 2 characters.')
        return value

    def validate_phone(self, value):
        """Phone must be unique and in a valid format."""
        value = sanitize(value).replace(' ', '').replace('-', '')

        # Basic phone number check: starts with + or digit, 8-15 digits total
        if not value.lstrip('+').isdigit():
            raise serializers.ValidationError('Enter a valid phone number (digits only).')

        if len(value.lstrip('+')) < 8 or len(value.lstrip('+')) > 15:
            raise serializers.ValidationError('Phone number must be between 8 and 15 digits.')

        # Check uniqueness (also enforced by DB unique=True, but better to catch here)
        if CustomUser.objects.filter(phone=value).exists():
            raise serializers.ValidationError('An account with this phone number already exists.')

        return value

    def validate_location(self, value):
        return sanitize(value)

    # ── Object-level validation (checks multiple fields together) ──
    def validate(self, data):
        """Check that both passwords match."""
        if data['password'] != data.get('password_confirm'):
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        """
        Remove password_confirm before creating user.
        Django's create_user() will hash the password automatically.
        """
        validated_data.pop('password_confirm')
        return CustomUser.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """
    Validates login credentials.
    POST /api/auth/login/
    """
    phone    = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, data):
        phone    = sanitize(data.get('phone', '')).replace(' ', '')
        password = data.get('password', '')

        if not phone or not password:
            raise serializers.ValidationError('Phone number and password are required.')

        # Django's authenticate() checks password hash — safe against timing attacks
        user = authenticate(
            request=self.context.get('request'),
            username=phone,      # USERNAME_FIELD = 'phone', so this works
            password=password,
        )

        if not user:
            # Use a vague message — don't tell attacker if phone exists
            raise serializers.ValidationError(
                'Invalid phone number or password. Please try again.'
            )

        if not user.is_active:
            raise serializers.ValidationError('This account has been disabled.')

        data['user'] = user
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Returns user data in API responses.
    Only includes safe, non-sensitive fields.
    """
    class Meta:
        model  = CustomUser
        fields = ['id', 'name', 'phone', 'role', 'location', 'is_verified', 'date_joined']
        # id and date_joined are read-only — users cannot change these
        read_only_fields = ['id', 'phone', 'role', 'is_verified', 'date_joined']

    def update(self, instance, validated_data):
        """
        Allow users to update name and location only.
        Phone and role changes require admin action.
        """
        instance.name     = sanitize(validated_data.get('name', instance.name))
        instance.location = sanitize(validated_data.get('location', instance.location))
        instance.save()
        return instance
