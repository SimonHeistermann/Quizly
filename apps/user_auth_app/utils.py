from django.conf import settings


def cookie_settings():
    """
    Central place for JWT cookie settings.
    You can override these in settings.py if needed.
    """
    return {
        "httponly": True,
        "secure": getattr(settings, "SECURE_COOKIES", False),
        "samesite": getattr(settings, "JWT_COOKIE_SAMESITE", "Lax"),
        "path": getattr(settings, "JWT_COOKIE_PATH", "/"),
        "domain": getattr(settings, "JWT_COOKIE_DOMAIN", None),
    }


def set_access_cookie(response, token: str):
    response.set_cookie(key="access_token", value=token, **cookie_settings())


def set_refresh_cookie(response, token: str):
    response.set_cookie(key="refresh_token", value=token, **cookie_settings())


def clear_jwt_cookies(response):
    opts = cookie_settings()
    response.delete_cookie("access_token", path=opts["path"], domain=opts["domain"], samesite=opts["samesite"])
    response.delete_cookie("refresh_token", path=opts["path"], domain=opts["domain"], samesite=opts["samesite"])