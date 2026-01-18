"""
URL routing for the user authentication API.

Defines endpoints for:
- registration
- login (JWT in cookies)
- logout (clears cookies / blacklists refresh token best-effort)
- refresh access token (requires refresh token cookie)
"""

from django.urls import path

from .views import (
    RegistrationView,
    LogoutView,
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
)

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="register"),
    path("login/", CookieTokenObtainPairView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
]