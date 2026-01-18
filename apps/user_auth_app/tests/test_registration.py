"""
Registration endpoint tests for the user authentication API.

Verifies that:
- successful registration returns 201 and creates the user
- password mismatch is rejected with 400
- duplicate emails are rejected with 400
- missing required fields are rejected with 400
"""

from typing import Any, Mapping, cast

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.test import APITestCase

User = get_user_model()


class RegistrationTests(APITestCase):
    """
    Tests for POST /register/.
    """

    def setUp(self):
        self.url = reverse("register")

    def test_registration_success_returns_201_and_detail(self):
        payload = {
            "username": "newuser",
            "email": "new@user.de",
            "password": "Newpassword123!",
            "confirmed_password": "Newpassword123!",
        }
        response = cast(Response, self.client.post(self.url, payload, format="json"))
        data = cast(Mapping[str, Any], response.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data["detail"], "User created successfully!")
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_registration_password_mismatch_returns_400(self):
        payload = {
            "username": "newuser",
            "email": "new@user.de",
            "password": "Newpassword123!",
            "confirmed_password": "Differentpassword123!",
        }
        response = cast(Response, self.client.post(self.url, payload, format="json"))
        data = cast(Mapping[str, Any], response.data)

        self.assertEqual(response.status_code, 400)
        self.assertIn("confirmed_password", data)

    def test_registration_duplicate_email_returns_400(self):
        User.objects.create_user(username="u1", email="dup@user.de", password="Somepass123!")

        payload = {
            "username": "newuser",
            "email": "dup@user.de",
            "password": "Newpassword123!",
            "confirmed_password": "Newpassword123!",
        }
        response = cast(Response, self.client.post(self.url, payload, format="json"))
        data = cast(Mapping[str, Any], response.data)

        self.assertEqual(response.status_code, 400)
        self.assertIn("email", data)

    def test_registration_missing_fields_returns_400(self):
        payload = {
            "username": "newuser",
            "email": "new@user.de",
            "confirmed_password": "Newpassword123!",
        }
        response = cast(Response, self.client.post(self.url, payload, format="json"))
        data = cast(Mapping[str, Any], response.data)

        self.assertEqual(response.status_code, 400)
        self.assertIn("password", data)