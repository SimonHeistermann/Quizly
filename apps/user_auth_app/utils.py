"""
Cookie utilities for JWT-based authentication.

Centralizes cookie configuration and provides helpers to set and clear JWT cookies
(access and refresh tokens) on DRF/Django responses.
"""

from django.conf import settings


def cookie_settings():
    """
    Return a dictionary of common cookie options for JWT cookies.

    Settings can be overridden via Django settings:
    - SECURE_COOKIES
    - JWT_COOKIE_SAMESITE
    - JWT_COOKIE_PATH
    - JWT_COOKIE_DOMAIN
    """
    return {
        "httponly": True,
        "secure": getattr(settings, "SECURE_COOKIES", False),
        "samesite": getattr(settings, "JWT_COOKIE_SAMESITE", "Lax"),
        "path": getattr(settings, "JWT_COOKIE_PATH", "/"),
        "domain": getattr(settings, "JWT_COOKIE_DOMAIN", None),
    }


def set_access_cookie(response, token: str):
    """
    Set the access token cookie on the given response.
    """
    response.set_cookie(key="access_token", value=token, **cookie_settings())


def set_refresh_cookie(response, token: str):
    """
    Set the refresh token cookie on the given response.
    """
    response.set_cookie(key="refresh_token", value=token, **cookie_settings())


def clear_jwt_cookies(response):
    """
    Clear both access and refresh token cookies from the response.
    """
    opts = cookie_settings()
    response.delete_cookie("access_token", path=opts["path"], domain=opts["domain"], samesite=opts["samesite"])
    response.delete_cookie("refresh_token", path=opts["path"], domain=opts["domain"], samesite=opts["samesite"])