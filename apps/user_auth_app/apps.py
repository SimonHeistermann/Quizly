"""
App configuration for the user authentication app.

Defines Django application metadata such as the default primary key field type
and the full Python path to the app package.
"""

from django.apps import AppConfig


class UserAuthConfig(AppConfig):
    """
    Django AppConfig for the user authentication application.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.user_auth_app"