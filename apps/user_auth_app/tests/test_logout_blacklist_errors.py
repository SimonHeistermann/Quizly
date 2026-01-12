from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

User = get_user_model()


class LogoutBlacklistErrorPathTests(APITestCase):
    def setUp(self):
        self.login_url = reverse("login")
        self.logout_url = reverse("logout")
        self.user = User.objects.create_user(
            username="blacklistuser",
            email="blacklistuser@example.com",
            password="Password123!",
        )

    def _login_and_set_client_cookies(self):
        resp = self.client.post(
            self.login_url,
            {"username": "blacklistuser", "password": "Password123!"},
            format="json",
        )
        self.client.cookies["access_token"] = resp.cookies["access_token"].value
        self.client.cookies["refresh_token"] = resp.cookies["refresh_token"].value
        return resp

    def test_logout_still_succeeds_when_blacklist_raises_unexpected_exception(self):
        self._login_and_set_client_cookies()

        with patch("apps.user_auth_app.api.views.RefreshToken.blacklist", side_effect=Exception("boom")):
            response = self.client.post(self.logout_url, {}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)
        self.assertEqual(response.cookies["access_token"].value, "")
        self.assertEqual(response.cookies["refresh_token"].value, "")