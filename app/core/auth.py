from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

bearer_scheme = HTTPBearer(auto_error=False)


def _get_jwks_url() -> str | None:
    if settings.supabase_jwks_url:
        return settings.supabase_jwks_url
    if settings.supabase_url:
        return f"{settings.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
    return None


def _auth_error(message: str = "Invalid or expired token.") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=message,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _settings_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Supabase auth is not configured.",
    )


def _decode_with_jwks(token: str, jwks_url: str) -> dict[str, Any]:
    try:
        import jwt
        from jwt import PyJWKClient
    except ImportError as exc:
        raise _settings_error() from exc

    signing_key = PyJWKClient(jwks_url).get_signing_key_from_jwt(token)
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256", "ES256"],
        audience=settings.supabase_jwt_audience,
        options={"verify_aud": bool(settings.supabase_jwt_audience)},
    )


def _decode_with_legacy_secret(token: str, jwt_secret: str) -> dict[str, Any]:
    try:
        import jwt
    except ImportError as exc:
        raise _settings_error() from exc

    return jwt.decode(
        token,
        jwt_secret,
        algorithms=["HS256"],
        audience=settings.supabase_jwt_audience,
        options={"verify_aud": bool(settings.supabase_jwt_audience)},
    )


def verify_supabase_token(token: str) -> dict[str, Any]:
    try:
        jwks_url = _get_jwks_url()
        if jwks_url:
            return _decode_with_jwks(token, jwks_url)
        if settings.supabase_jwt_secret:
            return _decode_with_legacy_secret(token, settings.supabase_jwt_secret)
    except HTTPException:
        raise
    except Exception as exc:
        raise _auth_error() from exc

    raise _settings_error()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, Any]:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _auth_error("Missing bearer token.")

    claims = verify_supabase_token(credentials.credentials)
    return {
        "id": claims.get("sub"),
        "email": claims.get("email"),
        "claims": claims,
    }
