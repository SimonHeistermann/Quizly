"""
Tests for the CookieJWTAuthentication backend.

These tests validate that authentication correctly returns None when:
- no access_token cookie is present
- an invalid token is provided
"""

from typing import cast

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from apps.user_auth_app.authentication import CookieJWTAuthentication

User = get_user_model()


class CookieJWTAuthenticationTests(TestCase):
    """
    Unit tests for CookieJWTAuthentication.

    Note:
    APIRequestFactory returns a Django WSGIRequest, while DRF/JWTAuthentication
    type hints often expect a DRF Request. We cast for the type checker only.
    """

    def setUp(self):
        self.factory = APIRequestFactory()
        self.auth = CookieJWTAuthentication()

    def test_authenticate_returns_none_if_no_cookie(self):
        request = cast(Request, self.factory.get("/api/quizzes/"))
        result = self.auth.authenticate(request)
        self.assertIsNone(result)

    def test_authenticate_returns_none_for_invalid_token(self):
        request = cast(Request, self.factory.get("/api/quizzes/"))
        request.COOKIES["access_token"] = "invalidtoken"
        result = self.auth.authenticate(request)
        self.assertIsNone(result)