from rest_framework import permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


class AuthenticatedViaRefreshToken(permissions.BasePermission):
    """
    Allows access only if a valid refresh_token cookie exists.
    This is used for /api/token/refresh/.
    """

    message = "Refresh token invalid or missing."

    def has_permission(self, request, view):
        token = request.COOKIES.get("refresh_token")
        if not token:
            return False

        try:
            RefreshToken(token)
            return True
        except TokenError:
            return False
