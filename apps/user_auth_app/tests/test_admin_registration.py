from unittest.mock import patch

from django.test import SimpleTestCase


class AdminModuleImportTests(SimpleTestCase):
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