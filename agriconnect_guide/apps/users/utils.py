# ============================================================
# AgriConnect — Utility Functions
# apps/users/utils.py
# ============================================================

import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger('django.security')


def custom_exception_handler(exc, context):
    """
    Custom error response format.
    All errors from every endpoint look the same:

        { "success": false, "error": "message here" }

    This makes it much easier for the frontend to handle errors.
    """
    # Call the default DRF handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Flatten any nested error messages into one string
        errors = response.data

        if isinstance(errors, dict):
            # Pick the first error message from any field
            messages = []
            for key, value in errors.items():
                if isinstance(value, list):
                    messages.append(str(value[0]))
                else:
                    messages.append(str(value))
            error_message = ' '.join(messages)
        elif isinstance(errors, list):
            error_message = str(errors[0])
        else:
            error_message = str(errors)

        response.data = {
            'success': False,
            'error': error_message,
        }

    return response


def success_response(data=None, message='Success', status_code=status.HTTP_200_OK):
    """
    Consistent success response format:

        { "success": true, "message": "...", "data": { ... } }

    Import and use in views like:
        return success_response(data=serializer.data, message='Registered!')
    """
    payload = {
        'success': True,
        'message': message,
    }
    if data is not None:
        payload['data'] = data

    return Response(payload, status=status_code)


def validate_image(image_file):
    """
    Validate an uploaded image file.
    Checks file extension and size before saving.
    Returns (is_valid: bool, error_message: str)
    """
    if not image_file:
        return True, None  # Image is optional

    # Allowed file types
    ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']
    MAX_SIZE_MB = 5
    MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024

    # Check extension
    import os
    ext = os.path.splitext(image_file.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f'Only JPG, PNG, and WEBP images are allowed. Got: {ext}'

    # Check file size
    if image_file.size > MAX_SIZE_BYTES:
        return False, f'Image must be smaller than {MAX_SIZE_MB} MB.'

    return True, None
