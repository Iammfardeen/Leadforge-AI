"""
Auth dependency for FastAPI routes.

The frontend (Supabase Auth) issues a JWT to the browser. The browser sends
it as `Authorization: Bearer <token>` on every API call. This module verifies
that token and extracts the user id, so route handlers can scope every query
to `current_user.id` without trusting anything the client claims.
"""
from dataclasses import dataclass

import jwt
from fastapi import Header, HTTPException, status

from app.core.config import get_settings

settings = get_settings()


@dataclass
class CurrentUser:
    id: str
    email: str | None = None


def get_current_user(authorization: str | None = Header(default=None)) -> CurrentUser:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header",
        )

    token = authorization.split(" ", 1)[1]

    if not settings.SUPABASE_JWT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SUPABASE_JWT_SECRET is not configured on the backend",
        )

    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {exc}",
        ) from exc

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject claim",
        )

    return CurrentUser(id=user_id, email=payload.get("email"))
