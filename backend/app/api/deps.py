import hmac

from fastapi import Header, HTTPException

from app.config.settings import settings
from app.services.auth.jwt_tokens import decode_token
from app.services.auth.users_repo import get_user_by_id


def _bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    parts = authorization.split(" ", 1)
    if len(parts) != 2:
        return None
    if parts[0].lower() != "bearer":
        return None
    return parts[1].strip() or None


def get_current_user(authorization: str | None = Header(default=None)):
    token = _bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="missing token")
    try:
        data = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="invalid token")
    if data.get("type") != "access":
        raise HTTPException(status_code=401, detail="invalid token")
    try:
        user_id = int(data.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="invalid token")
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="invalid token")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="user disabled")
    return user


def require_admin(authorization: str | None = Header(default=None)):
    user = get_current_user(authorization)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="forbidden")
    return user


def require_engine_access(
    authorization: str | None = Header(default=None),
    x_internal_key: str | None = Header(default=None, alias="X-Internal-Key"),
):
    """Allow either user JWT auth or trusted inter-service key auth.

    Inter-service access supports:
    - Authorization: Bearer <KB_API_KEY|ADMIN_API_KEY>
    - X-Internal-Key: <KB_API_KEY|ADMIN_API_KEY>
    """
    bearer = _bearer_token(authorization)

    # 1) First, try regular user auth (JWT access token).
    if bearer:
        try:
            return get_current_user(authorization)
        except HTTPException:
            # Continue with service-key checks.
            pass

    # 2) Service-to-service auth.
    service_candidates = [
        (settings.admin_api_key.get_secret_value() or "").strip(),
    ]
    # Optional dedicated key; if absent, fallback to admin_api_key only.
    kb_service_key = (settings.kb_api_key.get_secret_value() or "").strip()
    if kb_service_key:
        service_candidates.append(kb_service_key)

    provided = (x_internal_key or bearer or "").strip()
    if provided and any(
        candidate and hmac.compare_digest(provided, candidate)
        for candidate in service_candidates
    ):
        return {"auth_type": "service"}

    raise HTTPException(status_code=401, detail="invalid token")
