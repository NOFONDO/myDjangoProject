# ============================================================
# AgriConnect — Custom Permissions
# apps/users/permissions.py
#
# Permissions control WHO can do WHAT.
# We check the user's role before allowing sensitive actions.
# ============================================================

from rest_framework.permissions import BasePermission


class IsFarmer(BasePermission):
    """
    Allow access only to users with the 'farmer' role.
    Used on: product upload, edit, delete endpoints.
    """
    message = 'Only farmers can perform this action.'

    def has_permission(self, request, view):
        # User must be logged in AND be a farmer
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == 'farmer'
        )


class IsBuyer(BasePermission):
    """
    Allow access only to users with the 'buyer' role.
    Used on: placing orders.
    """
    message = 'Only buyers can perform this action.'

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == 'buyer'
        )


class IsFarmerOrReadOnly(BasePermission):
    """
    Farmers can create/edit/delete.
    Anyone logged in can read (GET requests).
    """
    message = 'Only farmers can modify products.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        # Safe methods (GET, HEAD, OPTIONS) allowed for everyone logged in
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        # Write methods only for farmers
        return request.user.role == 'farmer'


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level permission:
    Only the owner of an object (or an admin) can edit or delete it.
    Used to prevent farmer A from deleting farmer B's product.
    """
    message = 'You do not have permission to modify this item.'

    def has_object_permission(self, request, view, obj):
        # Admin can do anything
        if request.user.is_staff:
            return True
        # Owner check: obj.farmer == request.user
        # Works for Product (obj.farmer) and Order (obj.buyer)
        owner = getattr(obj, 'farmer', None) or getattr(obj, 'buyer', None)
        return owner == request.user
