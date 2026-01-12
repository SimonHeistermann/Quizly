from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

User = get_user_model()


class RegistrationTests(APITestCase):
    def setUp(self):
        self.url = reverse("register")

    def test_registration_success_returns_201_and_detail(self):
        payload = {
            "username": "newuser",
            "email": "new@user.de",
            "password": "Newpassword123!",
            "confirmed_password": "Newpassword123!",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["detail"], "User created successfully!")
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_registration_password_mismatch_returns_400(self):
        payload = {
            "username": "newuser",
            "email": "new@user.de",
            "password": "Newpassword123!",
            "confirmed_password": "Differentpassword123!",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("confirmed_password", response.data)

    def test_registration_duplicate_email_returns_400(self):
        User.objects.create_user(username="u1", email="dup@user.de", password="Somepass123!")

        payload = {
            "username": "newuser",
            "email": "dup@user.de",
            "password": "Newpassword123!",
            "confirmed_password": "Newpassword123!",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)

    def test_registration_missing_fields_returns_400(self):
        payload = {
            "username": "newuser",
            "email": "new@user.de",
            "confirmed_password": "Newpassword123!",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("password", response.data)