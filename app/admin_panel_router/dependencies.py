from __future__ import annotations

from typing import Optional, Dict

from fastapi import Cookie, HTTPException, status
from jose import JWTError, jwt

from app.api_router.schemas import AdminTokenData
from app.config import settings


ADMIN_AUTH_COOKIE_NAME = "admin_token"


def _check_permission_level(user_level: str, required_level: str) -> bool:
    levels = {"forbidden": 0, "viewer": 1, "editor": 2}
    return levels.get(user_level, 0) >= levels.get(required_level, 0)


async def require_admin_cookie(
    required_permissions: Optional[Dict[str, str]],
    admin_token: Optional[str],
) -> AdminTokenData:
    required_permissions = required_permissions or {}

    credentials_exception = HTTPException(
        status_code=status.HTTP_303_SEE_OTHER,
        detail="Not authenticated",
        headers={"Location": "/admin/login"},
    )
    forbidden_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You don't have permission to access this resource",
    )

    if not admin_token:
        raise credentials_exception

    try:
        payload = jwt.decode(
            admin_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        if payload.get("type") != "admin":
            raise credentials_exception

        login = payload.get("sub")
        super_user = payload.get("super_user", False)
        permissions = payload.get("permissions", {}) or {}

        token_data = AdminTokenData(
            login=login,
            super_user=super_user,
            permissions=permissions,
        )

        if super_user:
            return token_data

        for resource, required_level in required_permissions.items():
            user_level = permissions.get(resource, "forbidden")
            if not _check_permission_level(user_level, required_level):
                raise forbidden_exception

        return token_data
    except JWTError:
        raise credentials_exception


def _build_admin_dependency(required_permissions: Optional[Dict[str, str]] = None):
    async def dependency(
        admin_token: Optional[str] = Cookie(default=None, alias=ADMIN_AUTH_COOKIE_NAME),
    ) -> AdminTokenData:
        return await require_admin_cookie(required_permissions, admin_token)

    return dependency


def require_any_admin_cookie():
    return _build_admin_dependency()


def require_viewer_cookie(resource: str):
    return _build_admin_dependency({resource: "viewer"})


def require_editor_cookie(resource: str):
    return _build_admin_dependency({resource: "editor"})

