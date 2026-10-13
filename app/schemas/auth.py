import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, ConfigDict, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    tenant_slug: Optional[str] = Field(None, alias="tenantSlug")
    remember_me: Optional[bool] = Field(False, alias="rememberMe")

    model_config = ConfigDict(populate_by_name=True)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]


class RefreshTokenRequest(BaseModel):
    refresh_token: Optional[str] = None


class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = None


class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    tenant_slug: Optional[str] = Field(None, alias="tenantSlug")

    model_config = ConfigDict(populate_by_name=True)


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


class PublicTenantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    domain: Optional[str] = None
    logo_url: Optional[str] = None


class UserMeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    email: str
    first_name: str
    last_name: str
    role: str
    avatar_url: Optional[str] = None
    status: str
    last_login_at: Optional[datetime] = None
    tenant: Optional[Dict[str, Any]] = None
    tenant_settings: Optional[Dict[str, Any]] = None
    profile: Optional[Dict[str, Any]] = None
    permissions: List[str] = []
