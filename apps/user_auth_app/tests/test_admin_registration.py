"""
Tests for admin module registration behavior.

Ensures the admin module import is resilient when attempting to unregister a User
model that may not be registered yet (Django raises NotRegistered in that case).
"""

from unittest.mock import patch

from django.test import SimpleTestCase


class AdminModuleImportTests(SimpleTestCase):
    """
    Import-time behavior tests for the admin module.
    """

    def test_admin_unregister_handles_not_registered(self):
        from django.contrib.admin.sites import NotRegistered

        with patch("django.contrib.admin.sites.AdminSite.unregister") as mock_unreg, patch(
            "django.contrib.admin.sites.AdminSite.register"
        ) as mock_reg:
            mock_unreg.side_effect = NotRegistered("not registered")
            mock_reg.return_value = None

            import importlib
            import apps.user_auth_app.admin as admin_module

            importlib.reload(admin_module)

        self.assertTrue(True)