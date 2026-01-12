from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

User = get_user_model()


class LoginTests(APITestCase):
    def setUp(self):
        self.url = reverse("login")
        self.user = User.objects.create_user(
            username="olivia",
            email="olivia@example.com",
            password="Password123!",
        )

    def test_login_success_sets_cookies_and_returns_user_payload(self):
        response = self.client.post(
            self.url,
            {"username": "olivia", "password": "Password123!"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["detail"], "Login successfully!")
        self.assertEqual(response.data["user"]["username"], "olivia")
        self.assertEqual(response.data["user"]["email"], "olivia@example.com")

        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)
        self.assertTrue(response.cookies["access_token"].value)
        self.assertTrue(response.cookies["refresh_token"].value)

    def test_login_success_with_email_identifier(self):
        response = self.client.post(
            self.url,
            {"email": "olivia@example.com", "password": "Password123!"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)

    def test_login_missing_fields_returns_401(self):
        response = self.client.post(self.url, {"username": "olivia"}, format="json")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["detail"], "Invalid credentials.")

    def test_login_wrong_password_returns_401(self):
        response = self.client.post(
            self.url,
            {"username": "olivia", "password": "WrongPassword123!"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["detail"], "Invalid credentials.")