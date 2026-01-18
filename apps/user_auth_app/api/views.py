"""
API views for the user authentication app.

Implements a cookie-based JWT authentication flow using SimpleJWT:
- user registration
- login (issues access/refresh tokens as HttpOnly cookies)
- logout (clears cookies and best-effort blacklists refresh token)
- token refresh (requires a valid refresh token cookie)
"""

import logging
from typing import Any, Optional, cast

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import AbstractBaseUser
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .permissions import AuthenticatedViaRefreshToken
from .serializers import RegistrationSerializer
from ..utils import set_access_cookie, set_refresh_cookie, clear_jwt_cookies

logger = logging.getLogger(__name__)
User = get_user_model()


class RegistrationView(CreateAPIView):
    """
    Register a new user account.

    Validates registration input and creates the user via RegistrationSerializer.
    """

    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):
        """
        Handle POST requests for user registration.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "User created successfully!"}, status=status.HTTP_201_CREATED)


class CookieTokenObtainPairView(APIView):
    """
    Authenticate a user and set JWT tokens as cookies.

    Accepts either email or username as identifier and a password.
    On success, returns basic user info and sets access/refresh cookies.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle POST requests for login.

        Expects "email" or "username" and "password" in the request body.
        """
        identifier = request.data.get("email") or request.data.get("username")
        password = request.data.get("password")

        if not identifier or not password:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        user = self._authenticate(str(identifier), str(password))
        if user is None:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        user_id = getattr(user, "id", None)
        username = getattr(user, "username", "")
        email = getattr(user, "email", "")

        response = Response(
            {
                "detail": "Login successfully!",
                "user": {"id": user_id, "username": username, "email": email},
            },
            status=status.HTTP_200_OK,
        )
        set_access_cookie(response, str(access))
        set_refresh_cookie(response, str(refresh))
        return response

    def _authenticate(self, identifier: str, password: str) -> Optional[AbstractBaseUser]:
        """
        Authenticate a user using either email or username.

        If identifier contains "@", it is treated as an email and resolved to a username,
        since Django's default authenticate() uses username by default.
        """
        if "@" in identifier:
            user_obj = User.objects.filter(email__iexact=identifier).first()
            if not user_obj:
                return None
            return authenticate(username=getattr(user_obj, "username", ""), password=password)
        return authenticate(username=identifier, password=password)


class LogoutView(APIView):
    """
    Log out the authenticated user.

    Performs best-effort refresh token blacklisting (if present) and clears
    JWT cookies from the response.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Handle POST requests for logout.
        """
        refresh_token = request.COOKIES.get("refresh_token")
        if isinstance(refresh_token, str) and refresh_token.strip():
            self._blacklist_refresh(refresh_token)

        response = Response(
            {"detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."},
            status=status.HTTP_200_OK,
        )
        clear_jwt_cookies(response)
        return response

    def _blacklist_refresh(self, token: str) -> None:
        """
        Best-effort refresh token blacklist.

        Logout should still succeed even if token is expired/invalid/already blacklisted.
        """
        token = token.strip()
        if not token:
            return

        try:
            RefreshTokenCtor = cast(Any, RefreshToken)
            RefreshTokenCtor(token).blacklist()
        except TokenError:
            return
        except Exception:
            logger.exception("Unexpected error while blacklisting refresh token.")
            return


class CookieTokenRefreshView(TokenRefreshView):
    """
    Refresh an access token using the refresh token stored in cookies.

    Requires AuthenticatedViaRefreshToken permission, then validates the refresh
    token and sets a new access token cookie.
    """

    permission_classes = [AuthenticatedViaRefreshToken]

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to refresh the access token via refresh token cookie.
        """
        refresh_token = request.COOKIES.get("refresh_token")
        serializer = self.get_serializer(data={"refresh": refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            return Response({"detail": "Refresh token invalid or expired."}, status=status.HTTP_401_UNAUTHORIZED)

        access_token = serializer.validated_data.get("access")
        response = Response({"detail": "Token refreshed", "access": access_token}, status=status.HTTP_200_OK)
        set_access_cookie(response, access_token)
        return response