# ============================================================
# AgriConnect — Production Settings
# config/settings/production.py
#
# Used when deploying to a real server.
# Set DJANGO_SETTINGS_MODULE=config.settings.production
# ============================================================

from .base import *  # noqa: F401, F403

# ── Production Security ─────────────────────────────────────
DEBUG = False   # CRITICAL: Must be False in production

# ── HTTPS Security Headers ─────────────────────────────────
# Tell browsers to only connect via HTTPS
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000          # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Prevent cookies being sent over HTTP
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Prevent clickjacking attacks
X_FRAME_OPTIONS = 'DENY'

# Prevent browsers from guessing content type
SECURE_CONTENT_TYPE_NOSNIFF = True

# Enable browser XSS protection
SECURE_BROWSER_XSS_FILTER = True

# Referrer policy
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# ── Production Database — Use PostgreSQL ───────────────────
# Uncomment and configure when deploying:
#
# import dj_database_url
# DATABASES = {
#     'default': dj_database_url.config(
#         default=config('DATABASE_URL'),
#         conn_max_age=600,
#         ssl_require=True,
#     )
# }

# ── Production Email ────────────────────────────────────────
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = config('EMAIL_HOST')
# EMAIL_PORT = config('EMAIL_PORT', cast=int)
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = config('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
# DEFAULT_FROM_EMAIL = 'AgriConnect <noreply@agriconnect.cm>'
