"""
Root URL configuration for the Django project.

This module defines the top-level URL routing:
- Django admin interface
- User authentication API
- Quiz management API

All API endpoints are namespaced under the /api/ path.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.user_auth_app.api.urls")),
    path("api/", include("apps.quiz_management_app.api.urls")),
]