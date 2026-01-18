"""
App configuration for the quiz management app.

Defines Django application metadata such as the default primary key field type
and the full Python path to the app package.
"""

from django.apps import AppConfig


class QuizManagementConfig(AppConfig):
    """
    Django AppConfig for the quiz management application.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.quiz_management_app"