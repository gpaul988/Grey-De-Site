from rest_framework.permissions import BasePermission, IsAuthenticated

class IsSuperAdmin(BasePermission):
    """Allows access only to Super Admins"""

    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class IsAdminOrSuperAdmin(BasePermission):
    """Allows access to Admins and Super Admins"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'super_admin']

class IsAdminUser(BasePermission):
    """Allows access to admins and users"""

    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsSameCompany(BasePermission):
    """Allows access if user belongs to the same company"""


    def has_object_permission(self, request, view, obj):
        return request.user.role in ['admin', 'super_admin'] and request.user.company == obj.company