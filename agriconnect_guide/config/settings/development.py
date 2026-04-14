# ============================================================
# AgriConnect — Development Settings
# config/settings/development.py
#
# Use this when building/testing locally.
# Run with: python manage.py runserver --settings=config.settings.development
# OR set DJANGO_SETTINGS_MODULE=config.settings.development in .env
# ============================================================

from .base import *  # noqa: F401, F403 — import all base settings

# Development: show detailed error pages (NEVER in production)
DEBUG = True

# Allow local development hosts
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '0.0.0.0']

# ── Development-only installed apps ────────────────────────
# django-extensions gives useful tools like shell_plus
# Uncomment if you install it: pip install django-extensions
# INSTALLED_APPS += ['django_extensions']


# ── Relax rate limiting in development ─────────────────────
# So you don't get locked out while testing
REST_FRAMEWORK = {
    **REST_FRAMEWORK,   # inherit all base settings
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1000/hour',
        'user': '10000/hour',
        'login': '100/hour',
    },
}

# ── Relax axes lockout in development ──────────────────────
AXES_FAILURE_LIMIT = 100    # Don't lock out during development

# ── Email — just print emails to console in development ────
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ── CORS — allow all origins in development ────────────────
# WARNING: Never use this in production
CORS_ALLOW_ALL_ORIGINS = True
