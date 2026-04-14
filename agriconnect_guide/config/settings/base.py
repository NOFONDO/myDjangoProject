# ============================================================
# AgriConnect — Base Settings (shared by dev and production)
# config/settings/base.py
# ============================================================

import os
from pathlib import Path
from decouple import config, Csv

# ── Base directory ──────────────────────────────────────────
# Points to the /backend folder
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# ── Security — loaded from .env, never hardcoded ───────────
SECRET_KEY = config('SECRET_KEY')

# SECURITY: Always False in production (set in production.py)
DEBUG = config('DEBUG', default=False, cast=bool)

# Only allow listed hosts to receive requests
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost', cast=Csv())


# ── Installed Apps ──────────────────────────────────────────
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',               # Django REST Framework
    'rest_framework.authtoken',     # Token authentication
    'corsheaders',                  # Allow frontend to call API
    'axes',                         # Login attempt tracking / lockout
]

LOCAL_APPS = [
    'apps.users',       # Our custom user app
    'apps.products',    # Products and orders app
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# ── Middleware ──────────────────────────────────────────────
# ORDER MATTERS — security middleware goes first
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',    # Serve static files securely
    'corsheaders.middleware.CorsMiddleware',         # CORS must be near the top
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',               # Brute-force lockout
]


# ── URL Configuration ───────────────────────────────────────
ROOT_URLCONF = 'config.urls'


# ── Templates ───────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# ── Database ────────────────────────────────────────────────
# SQLite for development — simple, no extra setup needed
# Switch to PostgreSQL for production (see production.py)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ── Custom User Model ───────────────────────────────────────
# IMPORTANT: Must be set before the first migration
AUTH_USER_MODEL = 'users.CustomUser'


# ── Password Validation ─────────────────────────────────────
# Django enforces these rules on all passwords
AUTH_PASSWORD_VALIDATORS = [
    {
        # Password cannot be too similar to username/email
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        # Minimum 8 characters
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {
        # Not a common password like "password123"
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        # Must not be entirely numeric
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ── Django REST Framework Settings ─────────────────────────
REST_FRAMEWORK = {
    # Every API endpoint requires a valid token by default
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    # Must be logged in unless endpoint explicitly allows public access
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # Throttle/rate limiting — prevents abuse
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',   # unauthenticated users
        'rest_framework.throttling.UserRateThrottle',   # authenticated users
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '50/hour',      # anonymous: max 50 requests/hour
        'user': '500/hour',     # logged-in: max 500 requests/hour
        'login': '10/hour',     # custom — login endpoint: max 10 attempts/hour
    },
    # Consistent error response format
    'EXCEPTION_HANDLER': 'apps.users.utils.custom_exception_handler',
}


# ── django-axes: Brute Force Protection ────────────────────
# Locks out users/IPs after too many failed login attempts
AXES_FAILURE_LIMIT = 5              # Lock after 5 failed attempts
AXES_COOLOFF_TIME = 1               # Lock for 1 hour
AXES_LOCKOUT_CALLABLE = None        # Use default lockout response
AXES_RESET_ON_SUCCESS = True        # Reset fail count on successful login
AXES_ENABLE_ACCESS_FAILURE_LOG = True

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',   # Must be first
    'django.contrib.auth.backends.ModelBackend',
]


# ── CORS (Cross-Origin Resource Sharing) ───────────────────
# Tells the browser which frontend URLs are allowed to call our API
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://127.0.0.1:5500,http://localhost:5500',
    cast=Csv()
)
# Allow the browser to send cookies/auth headers cross-origin
CORS_ALLOW_CREDENTIALS = True

# Which HTTP headers the frontend is allowed to send
CORS_ALLOW_HEADERS = [
    'accept',
    'authorization',
    'content-type',
    'origin',
    'x-csrftoken',
]


# ── Internationalization ────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Douala'     # Cameroonian timezone
USE_I18N = True
USE_TZ = True


# ── Static and Media Files ──────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files = uploaded images from farmers
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Limit uploaded file size to 5 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5 MB


# ── Default primary key type ────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ── Logging ─────────────────────────────────────────────────
# Records security events (failed logins, errors) to a file
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.security': {
            'handlers': ['file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'axes': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
