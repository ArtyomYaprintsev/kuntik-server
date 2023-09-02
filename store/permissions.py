from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthenticatedOrListOnlyPermission(BasePermission):
    """

    If user is unauthenticated allows access only for queryset-level safe
    methods.

    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_authenticated


class IsAuthenticatedOrCreateRetrievePermission(BasePermission):
    """

    If user is unauthenticated allows access for `HEAD`, `OPTIONS` methods
    and `create` or `retrieve` actions.

    """
    def has_permission(self, request, view):
        if request.method in ("POST", "HEAD", "OPTIONS"):
            return True

        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return request.user and request.user.is_authenticated
