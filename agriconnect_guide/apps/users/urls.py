# ============================================================
# AgriConnect — User URL Patterns
# apps/users/urls.py
# ============================================================
from apps.users.views import home


from django.urls import path
from . import views

# All these are prefixed with /api/auth/ (set in config/urls.py)path('', home, name='home'),

urlpatterns = [
    path('', home, name='home'),
    # POST /api/auth/register/  → Create account
    path('register/', views.register_view, name='auth-register'),



    # POST /api/auth/login/     → Get token
    path('login/', views.login_view, name='auth-login'),

    # POST /api/auth/logout/    → Invalidate token
    path('logout/', views.logout_view, name='auth-logout'),

    # GET  /api/auth/me/        → View profile
    # PATCH /api/auth/me/       → Update profile
    path('me/', views.profile_view, name='auth-profile'),
]
