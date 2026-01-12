from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from apps.user_auth_app.api.permissions import AuthenticatedViaRefreshToken

User = get_user_model()


class DummyView(APIView):
    permission_classes = [AuthenticatedViaRefreshToken]


class AuthenticatedViaRefreshTokenTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = AuthenticatedViaRefreshToken()
        self.view = DummyView()
        self.user = User.objects.create_user(username="u1", email="u1@example.com", password="Password123!")

    def test_denies_when_cookie_missing(self):
        request = self.factory.post("/api/token/refresh/")
        assert self.permission.has_permission(request, self.view) is False

    def test_denies_when_cookie_invalid(self):
        request = self.factory.post("/api/token/refresh/")
        request.COOKIES["refresh_token"] = "invalid"
        assert self.permission.has_permission(request, self.view) is False

    def test_allows_when_cookie_valid(self):
        refresh = RefreshToken.for_user(self.user)
        request = self.factory.post("/api/token/refresh/")
        request.COOKIES["refresh_token"] = str(refresh)
        assert self.permission.has_permission(request, self.view) is True