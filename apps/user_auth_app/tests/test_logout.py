from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

User = get_user_model()


class LogoutTests(APITestCase):
    def setUp(self):
        self.login_url = reverse("login")
        self.logout_url = reverse("logout")
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="Password123!",
        )

    def _login_and_set_client_cookies(self):
        resp = self.client.post(
            self.login_url,
            {"username": "testuser", "password": "Password123!"},
            format="json",
        )
        self.client.cookies["access_token"] = resp.cookies["access_token"].value
        self.client.cookies["refresh_token"] = resp.cookies["refresh_token"].value
        return resp

    def test_logout_requires_auth_returns_401_without_access_cookie(self):
        response = self.client.post(self.logout_url, {}, format="json")
        self.assertEqual(response.status_code, 401)

    def test_logout_success_returns_200_and_clears_cookies(self):
        self._login_and_set_client_cookies()
        response = self.client.post(self.logout_url, {}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("detail", response.data)

        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)
        self.assertEqual(response.cookies["access_token"].value, "")
        self.assertEqual(response.cookies["refresh_token"].value, "")

    def test_logout_with_invalid_refresh_cookie_still_succeeds(self):
        login_resp = self._login_and_set_client_cookies()

        self.client.cookies["refresh_token"] = "invalid"

        response = self.client.post(self.logout_url, {}, format="json")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.cookies["access_token"].value, "")
        self.assertEqual(response.cookies["refresh_token"].value, "")