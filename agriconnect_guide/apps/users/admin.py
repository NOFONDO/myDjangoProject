# ============================================================
# AgriConnect — User Admin Configuration
# apps/users/admin.py
# ============================================================

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Customizes how users appear in the /admin panel.
    """
    # Columns shown in the user list
    list_display  = ['phone', 'name', 'role', 'location', 'is_active', 'is_verified', 'date_joined']
    list_filter   = ['role', 'is_active', 'is_verified', 'date_joined']
    search_fields = ['phone', 'name', 'location']
    ordering      = ['-date_joined']

    # Fields shown when viewing/editing a user
    fieldsets = (
        ('Login Info',   {'fields': ('phone', 'password')}),
        ('Personal Info',{'fields': ('name', 'role', 'location')}),
        ('Status',       {'fields': ('is_active', 'is_verified', 'is_staff', 'is_superuser')}),
        ('Permissions',  {'fields': ('groups', 'user_permissions')}),
        ('Timestamps',   {'fields': ('date_joined', 'last_login')}),
    )

    # Fields shown when creating a user from the admin panel
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'name', 'role', 'location', 'password1', 'password2'),
        }),
    )

    # These fields cannot be edited from the admin
    readonly_fields = ['date_joined', 'last_login']
