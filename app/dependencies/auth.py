import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db, set_tenant_context
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.models.platform import User

security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
    db: Session = Depends(get_db)
) -> User:
    """Dependency that authenticates the user from JWT Bearer token and sets tenant RLS context."""
    if not credentials:
        raise UnauthorizedException("Missing authentication credentials")

    token = credentials.credentials
    try:
        payload = decode_token(token)
        user_id_str: str = payload.get("sub")
        if not user_id_str:
            raise UnauthorizedException("Invalid token payload: missing sub")
        user_id = uuid.UUID(user_id_str)
        tenant_id_str: Optional[str] = payload.get("tenant_id") or x_tenant_id
    except Exception as e:
        raise UnauthorizedException(f"Could not validate credentials: {str(e)}")

    user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
    if not user:
        raise UnauthorizedException("User not found or has been deactivated")

    if user.status != "ACTIVE":
        raise ForbiddenException(f"User account status is {user.status}")

    if user.locked_until and user.locked_until > datetime.now(timezone.utc):
        raise ForbiddenException("Account is temporarily locked due to failed attempts")

    # Set row-level tenant context on the database session
    set_tenant_context(db, user.tenant_id)
    return user


def require_roles(allowed_roles: List[str]):
    """Returns a dependency checking that the authenticated user has one of the allowed roles."""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise ForbiddenException(
                f"Action requires one of roles: {', '.join(allowed_roles)}. Current role: {current_user.role}"
            )
        return current_user
    return role_checker


get_current_admin = require_roles(["ADMIN"])
get_current_dean = require_roles(["DEAN"])
get_admin_or_dean = require_roles(["ADMIN", "DEAN"])
get_current_faculty = require_roles(["FACULTY"])
get_current_student = require_roles(["STUDENT"])
