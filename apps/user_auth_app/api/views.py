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
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "User created successfully!"}, status=status.HTTP_201_CREATED)


class CookieTokenObtainPairView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
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
        if "@" in identifier:
            user_obj = User.objects.filter(email__iexact=identifier).first()
            if not user_obj:
                return None
            return authenticate(username=getattr(user_obj, "username", ""), password=password)
        return authenticate(username=identifier, password=password)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
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
    permission_classes = [AuthenticatedViaRefreshToken]

    def post(self, request, *args, **kwargs):
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