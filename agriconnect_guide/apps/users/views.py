# ============================================================
# AgriConnect — User Views (API Endpoints)
# apps/users/views.py
#
# These are the functions that handle HTTP requests.
# Each view maps to a URL in users/urls.py
# ============================================================

import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import AnonRateThrottle
from rest_framework.authtoken.models import Token

from .models import CustomUser
from .serializers import RegisterSerializer, LoginSerializer, UserProfileSerializer
from .utils import success_response

logger = logging.getLogger('django.security')


# ── Custom throttle for login endpoint ──────────────────────
class LoginThrottle(AnonRateThrottle):
    """
    Stricter rate limit on login endpoint.
    Max 10 login attempts per hour per IP address.
    Prevents brute-force password attacks.
    """
    scope = 'login'


# ── REGISTER ────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([AllowAny])   # No token needed — user doesn't have one yet
def register_view(request):
    """
    Create a new user account.
    URL: POST /api/auth/register/

    Request body:
        {
            "name": "Emmanuel Ngwa",
            "phone": "+237600000000",
            "password": "securepassword",
            "password_confirm": "securepassword",
            "role": "farmer",
            "location": "Buea, SW"
        }

    Success response (201):
        { "success": true, "message": "...", "data": { "token": "...", "user": { ... } } }
    """
    serializer = RegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return success_response(
            data=serializer.errors,
            message='Validation failed.',
        ).__class__(
            {'success': False, 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Save the new user (password is automatically hashed inside create_user)
    user = serializer.save()

    # Create auth token for this user — returned so frontend can store it
    token, _ = Token.objects.get_or_create(user=user)

    # Log the registration (not the password!)
    logger.info(f'New user registered: {user.phone} role={user.role}')

    return success_response(
        data={
            'token': token.key,
            'user':  UserProfileSerializer(user).data,
        },
        message=f'Welcome to AgriConnect, {user.name}!',
        status_code=status.HTTP_201_CREATED,
    )


# ── LOGIN ────────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([LoginThrottle])   # Apply strict rate limiting
def login_view(request):
    """
    Authenticate a user and return their token.
    URL: POST /api/auth/login/

    Request body:
        { "phone": "+237600000000", "password": "securepassword" }

    Success response (200):
        { "success": true, "data": { "token": "...", "user": { ... } } }
    """
    serializer = LoginSerializer(data=request.data, context={'request': request})

    if not serializer.is_valid():
        # Log failed attempt (IP recorded by django-axes automatically)
        logger.warning(
            f'Failed login attempt for phone: {request.data.get("phone", "unknown")} '
            f'from IP: {request.META.get("REMOTE_ADDR")}'
        )
        from rest_framework.response import Response
        return Response(
            {'success': False, 'error': list(serializer.errors.values())[0][0]},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    user  = serializer.validated_data['user']
    token, _ = Token.objects.get_or_create(user=user)

    logger.info(f'User logged in: {user.phone}')

    return success_response(
        data={
            'token': token.key,
            'user':  UserProfileSerializer(user).data,
        },
        message=f'Welcome back, {user.name}!',
    )


# ── LOGOUT ───────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Delete the user's auth token (logs them out).
    URL: POST /api/auth/logout/
    Header: Authorization: Token <token>
    """
    # Delete the token — it's now invalid even if someone stole it
    request.user.auth_token.delete()
    logger.info(f'User logged out: {request.user.phone}')
    return success_response(message='You have been logged out successfully.')


# ── GET/UPDATE PROFILE ───────────────────────────────────────
@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    GET  — Return the logged-in user's profile.
    PATCH — Update name or location only.
    URL: /api/auth/me/
    Header: Authorization: Token <token>
    """
    if request.method == 'GET':
        serializer = UserProfileSerializer(request.user)
        return success_response(data=serializer.data)

    # PATCH — partial update
    serializer = UserProfileSerializer(
        request.user,
        data=request.data,
        partial=True,   # Don't require all fields — only what's sent
    )
    if not serializer.is_valid():
        from rest_framework.response import Response
        return Response(
            {'success': False, 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer.save()
    return success_response(
        data=serializer.data,
        message='Profile updated successfully.',
    )

    from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to the E-Agriculture Backend!")
