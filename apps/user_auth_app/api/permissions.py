"""
Custom DRF permissions for the user authentication API.

Contains permission classes that enforce cookie-based JWT authentication flows,
e.g. ensuring a valid refresh token cookie is present for token refresh requests.
"""

from rest_framework import permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


class AuthenticatedViaRefreshToken(permissions.BasePermission):
    """
    Permission that allows access only if a valid refresh token cookie exists.

    This is intended for endpoints like /api/token/refresh/ where the refresh token
    is expected to be sent via the "refresh_token" cookie rather than request body.
    """

    message = "Refresh token invalid or missing."

    def has_permission(self, request, view):
        """
        Return True if the request includes a valid refresh token cookie.
        """
        token = request.COOKIES.get("refresh_token")
        if not token:
            return False

        try:
            RefreshToken(token)
            return True
        except TokenError:
            return False