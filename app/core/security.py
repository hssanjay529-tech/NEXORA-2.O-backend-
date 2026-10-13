import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import bcrypt
import jwt
from app.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a bcrypt hashed password string."""
    try:
        # Handle $2a$ / $2b$ / $2y$ prefix gracefully
        hash_bytes = hashed_password.encode('utf-8')
        if hashed_password.startswith("$2a$") or hashed_password.startswith("$2y$"):
            # standard bcrypt supports $2a$, $2b$
            hash_bytes = b"$2b$" + hash_bytes[4:]
        return bcrypt.checkpw(plain_password.encode('utf-8'), hash_bytes)
    except Exception:
        # Direct check attempt
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False


def get_password_hash(password: str) -> str:
    """Generates a bcrypt hash for the provided password."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Creates a signed JWT access token with tenant_id, role, and subject."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc), "jti": str(uuid.uuid4())})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Creates a long-lived JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc), "purpose": "REFRESH", "jti": str(uuid.uuid4())})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """Decodes and validates a JWT token."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
