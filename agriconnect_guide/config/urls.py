# ============================================================
# AgriConnect — Root URL Configuration
# config/urls.py
#
# All API routes start with /api/
# This keeps the API clean and separated from admin
# ============================================================

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse


# ── Simple health-check view ────────────────────────────────
def health_check(request):
    """
    A simple endpoint to confirm the API is running.
    Frontend can call GET /api/ to test connectivity.
    """
    return JsonResponse({
        'status': 'ok',
        'message': 'AgriConnect API is running.',
        'version': '1.0.0',
    })


urlpatterns = [
    # ── Django admin panel ──────────────────────────────────
    # Change 'admin/' to something less obvious in production
    path('admin/', admin.site.urls),

    # ── Health check ────────────────────────────────────────
    path('api/', health_check, name='health-check'),

    # ── Users API (register, login, profile) ────────────────
    path('api/auth/', include('apps.users.urls')),

    # ── Products API (list, create, detail, orders) ─────────
    path('api/products/', include('apps.products.urls')),
]

# ── Serve uploaded media files in development ───────────────
# In production, your web server (Nginx/Apache) serves media files.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
