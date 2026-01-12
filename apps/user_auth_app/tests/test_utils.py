from django.test import TestCase, override_settings
from rest_framework.response import Response

from apps.user_auth_app.utils import (
    set_access_cookie,
    set_refresh_cookie,
    clear_jwt_cookies,
)


class UtilsCookieTests(TestCase):
    @override_settings(SECURE_COOKIES=False, JWT_COOKIE_SAMESITE="Lax", JWT_COOKIE_PATH="/", JWT_COOKIE_DOMAIN=None)
    def test_set_access_and_refresh_cookie(self):
        resp = Response()
        set_access_cookie(resp, "access123")
        set_refresh_cookie(resp, "refresh123")

        self.assertIn("access_token", resp.cookies)
        self.assertIn("refresh_token", resp.cookies)

        self.assertEqual(resp.cookies["access_token"].value, "access123")
        self.assertEqual(resp.cookies["refresh_token"].value, "refresh123")

    @override_settings(SECURE_COOKIES=False, JWT_COOKIE_SAMESITE="Lax", JWT_COOKIE_PATH="/", JWT_COOKIE_DOMAIN=None)
    def test_clear_jwt_cookies_sets_deletion(self):
        resp = Response()
        clear_jwt_cookies(resp)

        self.assertIn("access_token", resp.cookies)
        self.assertIn("refresh_token", resp.cookies)
        self.assertEqual(resp.cookies["access_token"].value, "")
        self.assertEqual(resp.cookies["refresh_token"].value, "")
