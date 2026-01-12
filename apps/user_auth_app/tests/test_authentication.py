from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from apps.user_auth_app.authentication import CookieJWTAuthentication

User = get_user_model()


class CookieJWTAuthenticationTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.auth = CookieJWTAuthentication()

    def test_authenticate_returns_none_if_no_cookie(self):
        request = self.factory.get("/api/quizzes/")
        result = self.auth.authenticate(request)
        self.assertIsNone(result)

    def test_authenticate_returns_none_for_invalid_token(self):
        request = self.factory.get("/api/quizzes/")
        request.COOKIES["access_token"] = "invalidtoken"
        result = self.auth.authenticate(request)
        self.assertIsNone(result)