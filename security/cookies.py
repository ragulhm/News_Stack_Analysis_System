from fastapi import Response
from typing import Optional

COOKIE_NAME = "access_token"
COOKIE_MAX_AGE = 1440 * 60  # 24 hours

def set_access_cookie(response: Response, token: str):
    """Secure identity token persistence in browser cookie."""
    response.set_cookie(
        key=COOKIE_NAME,
        value=f"Bearer {token}",
        httponly=True,
        max_age=COOKIE_MAX_AGE,
        expires=COOKIE_MAX_AGE,
        samesite="lax",
        secure=False # Set to True for HTTPS environments
    )

def delete_access_cookie(response: Response):
    """Sever identity token link by clearing the cookie."""
    response.delete_cookie(key=COOKIE_NAME)
