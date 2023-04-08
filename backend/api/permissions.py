from rest_framework import permissions


class IsOwnerOrStaffOrReadOnly(permissions.BasePermission):
    """Доступ только владельцу или чтение."""

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS) or (
            request.user.is_authenticated
        )


def check_object_permissions(request, obj):
    return (request.method in permissions.SAFE_METHODS) or (
            obj.author == request.user or request.user.is_superuser
    )
