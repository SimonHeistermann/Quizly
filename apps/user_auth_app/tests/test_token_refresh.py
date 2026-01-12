from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

User = get_user_model()


class TokenRefreshTests(APITestCase):
    def setUp(self):
        self.login_url = reverse("login")
        self.refresh_url = reverse("token_refresh")
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="Password123!",
        )

    def _login_and_set_refresh_cookie(self):
        resp = self.client.post(
            self.login_url,
            {"username": "testuser", "password": "Password123!"},
            format="json",
        )
        self.client.cookies["refresh_token"] = resp.cookies["refresh_token"].value
        return resp

    def test_refresh_success_returns_200_and_sets_new_access_cookie(self):
        self._login_and_set_refresh_cookie()
        response = self.client.post(self.refresh_url, {}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["detail"], "Token refreshed")
        self.assertIn("access", response.data)

        self.assertIn("access_token", response.cookies)
        self.assertTrue(response.cookies["access_token"].value)

    def test_refresh_missing_cookie_returns_403_due_to_permission(self):
        response = self.client.post(self.refresh_url, {}, format="json")
        self.assertEqual(response.status_code, 403)

    def test_refresh_invalid_cookie_returns_403_or_401(self):
        self.client.cookies["refresh_token"] = "invalidtoken"
        response = self.client.post(self.refresh_url, {}, format="json")
        self.assertIn(response.status_code, (403, 401))
