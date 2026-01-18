"""
Login endpoint tests for the user authentication API.

Verifies that:
- valid credentials return a success payload and set JWT cookies
- login works with username or email identifiers
- invalid or incomplete credentials return 401 with a consistent error message
"""

from typing import Any, Mapping, cast

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.test import APITestCase

User = get_user_model()


class LoginTests(APITestCase):
    """
    Tests for POST /login/ (cookie-based JWT login).
    """

    def setUp(self):
        self.url = reverse("login")
        self.user = User.objects.create_user(
            username="olivia",
            email="olivia@example.com",
            password="Password123!",
        )

    def test_login_success_sets_cookies_and_returns_user_payload(self):
        response = cast(
            Response,
            self.client.post(
                self.url,
                {"username": "olivia", "password": "Password123!"},
                format="json",
            ),
        )
        data = cast(Mapping[str, Any], response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["detail"], "Login successfully!")
        self.assertEqual(cast(Mapping[str, Any], data["user"])["username"], "olivia")
        self.assertEqual(cast(Mapping[str, Any], data["user"])["email"], "olivia@example.com")

        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)
        self.assertTrue(response.cookies["access_token"].value)
        self.assertTrue(response.cookies["refresh_token"].value)

    def test_login_success_with_email_identifier(self):
        response = cast(
            Response,
            self.client.post(
                self.url,
                {"email": "olivia@example.com", "password": "Password123!"},
                format="json",
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)

    def test_login_missing_fields_returns_401(self):
        response = cast(Response, self.client.post(self.url, {"username": "olivia"}, format="json"))
        data = cast(Mapping[str, Any], response.data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(data["detail"], "Invalid credentials.")

    def test_login_wrong_password_returns_401(self):
        response = cast(
            Response,
            self.client.post(
                self.url,
                {"username": "olivia", "password": "WrongPassword123!"},
                format="json",
            ),
        )
        data = cast(Mapping[str, Any], response.data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(data["detail"], "Invalid credentials.")