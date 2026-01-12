from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

User = get_user_model()


class CookieJWTAuthentication(JWTAuthentication):
    """
    Authenticate using the access_token stored in an HttpOnly cookie.
    Compatible with DRF's IsAuthenticated permission.

    Behavior:
    - No cookie -> returns None (unauthenticated)
    - Invalid/expired token -> returns None (unauthenticated)
    """

    def authenticate(self, request):
        raw_token = request.COOKIES.get("access_token")
        if not raw_token:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
        except (InvalidToken, TokenError):
            return None

        return (user, validated_token)