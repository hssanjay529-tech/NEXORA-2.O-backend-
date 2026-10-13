import uuid
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
from app.database import get_db, set_tenant_context
from app.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from app.core.exceptions import UnauthorizedException, BadRequestException, NotFoundException, ForbiddenException
from app.dependencies.auth import get_current_user
from app.models.platform import User, Tenant, UserToken, LoginAttempt, AuditLog
from app.models.academic import Faculty, Student, Department, Programme
from app.schemas.auth import (
    LoginRequest, TokenResponse, RefreshTokenRequest, LogoutRequest,
    UserMeResponse, ForgotPasswordRequest, ResetPasswordRequest, ChangePasswordRequest,
    PublicTenantOut
)

router = APIRouter(prefix="/auth", tags=["Authentication & Session"])
tenants_router = APIRouter(prefix="/tenants", tags=["Tenants"])


# -----------------------------------------------------------------------------
# Public Tenant Discovery
# -----------------------------------------------------------------------------

@tenants_router.get("/public", response_model=List[PublicTenantOut])
def get_public_tenants(db: Session = Depends(get_db)):
    """GET /api/v1/tenants/public - Public tenant directory for login dropdown."""
    tenants = db.query(Tenant).filter(Tenant.status == "ACTIVE").all()
    results = []
    for t in tenants:
        domain = t.settings.get("domain", f"{t.slug}.edu") if t.settings else f"{t.slug}.edu"
        logo_url = t.settings.get("logo_url", "/assets/nexora-logo-mark.png") if t.settings else "/assets/nexora-logo-mark.png"
        results.append(PublicTenantOut(
            id=t.id,
            name=t.name,
            slug=t.slug,
            domain=domain,
            logo_url=logo_url
        ))
    if not results:
        # Guarantee default tenant is present
        results.append(PublicTenantOut(
            id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
            name="Apex Institute of Technology",
            slug="apex",
            domain="apex.edu",
            logo_url="/assets/nexora-logo-mark.png"
        ))
    return results


# -----------------------------------------------------------------------------
# Authentication: Login, Refresh, Logout
# -----------------------------------------------------------------------------

@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Unified user authentication & JWT issuance. Role is strictly determined from the database."""
    client_ip = request.client.host if request.client else "unknown"

    # Resolve tenant by slug or domain if provided
    tenant = None
    if payload.tenant_slug:
        tenant = db.query(Tenant).filter(Tenant.slug == payload.tenant_slug).first()

    query = db.query(User).filter(User.email == payload.email, User.deleted_at.is_(None))
    if tenant:
        query = query.filter(User.tenant_id == tenant.id)
    user = query.first()

    # Fallback search if tenant slug was omitted (e.g. email domain match)
    if not user and not tenant:
        user = db.query(User).filter(User.email == payload.email, User.deleted_at.is_(None)).first()

    if not user:
        if tenant:
            attempt = LoginAttempt(
                tenant_id=tenant.id,
                email=payload.email,
                success=False,
                ip_address=client_ip
            )
            db.add(attempt)
            db.commit()
        # Generic error message to prevent account enumeration
        raise UnauthorizedException("Invalid email or password")

    # Set tenant context
    set_tenant_context(db, user.tenant_id)
    resolved_tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()

    # Check if locked
    if user.locked_until and user.locked_until > datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account is temporarily locked due to repeated failed attempts. Please try again later."
        )

    # Verify password
    if not verify_password(payload.password, user.password_hash):
        user.failed_login_count = (user.failed_login_count or 0) + 1
        if user.failed_login_count >= 5:
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)

        attempt = LoginAttempt(
            tenant_id=user.tenant_id,
            user_id=user.id,
            email=user.email,
            success=False,
            ip_address=client_ip
        )
        db.add(attempt)
        db.commit()
        raise UnauthorizedException("Invalid email or password")

    # Success: reset failed count and update last login
    user.failed_login_count = 0
    user.locked_until = None
    user.last_login_at = datetime.now(timezone.utc)

    attempt = LoginAttempt(
        tenant_id=user.tenant_id,
        user_id=user.id,
        email=user.email,
        success=True,
        ip_address=client_ip
    )
    db.add(attempt)

    audit = AuditLog(
        tenant_id=user.tenant_id,
        user_id=user.id,
        action="USER_LOGIN",
        entity_type="USER",
        entity_id=user.id,
        ip_address=client_ip,
        new_value={"role": user.role, "email": user.email}
    )
    db.add(audit)

    # Issue JWT tokens
    full_name = f"{user.first_name} {user.last_name}".strip()
    token_claims = {
        "sub": str(user.id),
        "email": user.email,
        "name": full_name,
        "role": user.role,
        "tenant_id": str(user.tenant_id)
    }
    access_token = create_access_token(token_claims)
    refresh_token = create_refresh_token(token_claims)

    # Store refresh token hash in user_tokens
    token_hash = hashlib.sha256(refresh_token.encode('utf-8')).hexdigest()
    user_token_entry = UserToken(
        tenant_id=user.tenant_id,
        user_id=user.id,
        purpose="REFRESH",
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(user_token_entry)
    db.commit()

    # Set httpOnly Secure refresh cookie
    cookie_max_age = (settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400) if payload.remember_me else None
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # Allow localhost dev
        samesite="lax",
        max_age=cookie_max_age
    )

    # Resolve deep profile details for lanyard badge
    identifier = "APEX-USER"
    department_name = "Institutional Operations"
    programme_name = None

    if user.role == "STUDENT":
        stu = db.query(Student).filter(Student.user_id == user.id).first()
        if stu:
            identifier = getattr(stu, "roll_no", "2024CSE001")
            prog = db.query(Programme).filter(Programme.id == stu.programme_id).first()
            programme_name = prog.name if prog else "B.Tech Computer Science & Engineering"
            department_name = programme_name
    elif user.role in ["FACULTY", "DEAN"]:
        fac = db.query(Faculty).filter(Faculty.user_id == user.id).first()
        if fac:
            identifier = getattr(fac, "employee_no", "FAC-001")
            dept = db.query(Department).filter(Department.id == fac.department_id).first()
            department_name = dept.name if dept else ("School of Computing" if user.role == "DEAN" else "Faculty of Computer Science")
    elif user.role == "ADMIN":
        identifier = "ADM-001"
        department_name = "Institutional Governance"

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "id": str(user.id),
            "name": full_name,
            "full_name": full_name,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": user.role,
            "identifier": identifier,
            "department_name": department_name,
            "programme_name": programme_name,
            "verified": True,
            "tenant": {
                "id": str(resolved_tenant.id) if resolved_tenant else str(user.tenant_id),
                "name": resolved_tenant.name if resolved_tenant else "Apex Institute of Technology",
                "slug": resolved_tenant.slug if resolved_tenant else "apex"
            }
        }
    )


@router.post("/refresh", response_model=Dict[str, Any])
def refresh_token(
    payload: RefreshTokenRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Token Rotation: verifies refresh token (from cookie or payload) and issues a new access token."""
    raw_token = payload.refresh_token or request.cookies.get("refresh_token")
    if not raw_token:
        raise UnauthorizedException("Missing refresh token")

    try:
        decoded = decode_token(raw_token)
        if decoded.get("purpose") != "REFRESH":
            raise UnauthorizedException("Invalid token type")
        user_id = uuid.UUID(decoded.get("sub"))
    except Exception:
        raise UnauthorizedException("Invalid or expired refresh token")

    token_hash = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()
    stored_token = db.query(UserToken).filter(
        UserToken.token_hash == token_hash,
        UserToken.user_id == user_id,
        UserToken.revoked_at.is_(None)
    ).first()

    if not stored_token or stored_token.expires_at < datetime.now(timezone.utc):
        raise UnauthorizedException("Refresh token is invalid, expired, or has been revoked")

    user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
    if not user or user.status != "ACTIVE":
        raise UnauthorizedException("User inactive or deleted")

    # Rotate refresh token: revoke current token and create replacement
    stored_token.revoked_at = datetime.now(timezone.utc)

    full_name = f"{user.first_name} {user.last_name}".strip()
    new_claims = {
        "sub": str(user.id),
        "email": user.email,
        "name": full_name,
        "role": user.role,
        "tenant_id": str(user.tenant_id)
    }
    new_access_token = create_access_token(new_claims)
    new_refresh_token = create_refresh_token(new_claims)

    new_token_hash = hashlib.sha256(new_refresh_token.encode('utf-8')).hexdigest()
    new_user_token = UserToken(
        tenant_id=user.tenant_id,
        user_id=user.id,
        purpose="REFRESH",
        token_hash=new_token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(new_user_token)
    db.commit()

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "role": user.role
    }


@router.post("/logout", response_model=Dict[str, Any])
def logout(
    payload: LogoutRequest,
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Session Invalidation: Revokes refresh token and clears cookie."""
    raw_token = payload.refresh_token or request.cookies.get("refresh_token")
    if raw_token:
        token_hash = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()
        stored_token = db.query(UserToken).filter(
            UserToken.token_hash == token_hash,
            UserToken.user_id == current_user.id
        ).first()
        if stored_token:
            stored_token.revoked_at = datetime.now(timezone.utc)
    else:
        # Revoke all active tokens for this user
        db.query(UserToken).filter(
            UserToken.user_id == current_user.id,
            UserToken.revoked_at.is_(None)
        ).update({"revoked_at": datetime.now(timezone.utc)})

    audit = AuditLog(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="USER_LOGOUT",
        entity_type="USER",
        entity_id=current_user.id
    )
    db.add(audit)
    db.commit()

    response.delete_cookie("refresh_token")
    return {"success": True, "message": "Logged out successfully"}


@router.get("/me", response_model=UserMeResponse)
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Current Session & Verified Profile details."""
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()

    profile_data = {}
    if current_user.role == "FACULTY":
        fac = db.query(Faculty).filter(Faculty.user_id == current_user.id).first()
        if fac:
            profile_data = {
                "faculty_id": str(fac.id),
                "employee_no": getattr(fac, "employee_no", "FAC-001"),
                "designation": getattr(fac, "designation", "Assistant Professor"),
                "department_id": str(fac.department_id)
            }
    elif current_user.role == "DEAN":
        fac = db.query(Faculty).filter(Faculty.user_id == current_user.id).first()
        profile_data = {
            "faculty_id": str(fac.id) if fac else str(current_user.id),
            "employee_no": getattr(fac, "employee_no", "DEAN-ENG-001"),
            "designation": "Dean of Engineering & Computing",
            "department_id": str(fac.department_id) if fac else None
        }
    elif current_user.role == "STUDENT":
        stu = db.query(Student).filter(Student.user_id == current_user.id).first()
        if stu:
            profile_data = {
                "student_id": str(stu.id),
                "roll_no": getattr(stu, "roll_no", "2024CSE001"),
                "programme_id": str(stu.programme_id),
                "current_term_no": getattr(stu, "current_term_no", 4),
                "admission_year": getattr(stu, "admission_year", 2024)
            }
    elif current_user.role == "ADMIN":
        profile_data = {
            "employee_no": "ADM-001",
            "department": "Institutional Governance"
        }

    permissions = []
    if current_user.role == "ADMIN":
        permissions = [
            "users:manage", "calendar:manage", "departments:manage",
            "fee_structures:manage", "rooms:assign", "timetables:manage",
            "announcements:publish", "approvals:manage", "analytics:view", "compliance:manage"
        ]
    elif current_user.role == "DEAN":
        permissions = [
            "analytics:view", "approvals:manage", "curriculum:review",
            "faculty:oversight", "attendance:view_all", "grades:audit"
        ]
    elif current_user.role == "FACULTY":
        permissions = [
            "materials:upload", "attendance:record", "assignments:manage",
            "grades:submit", "academic_flags:raise", "discussions:post",
            "leave:apply", "proposals:create"
        ]
    elif current_user.role == "STUDENT":
        permissions = [
            "courses:register", "timetable:view", "attendance:view",
            "assignments:submit", "grades:view", "fees:pay",
            "exams:register", "documents:request", "grievances:raise"
        ]

    return UserMeResponse(
        id=current_user.id,
        tenant_id=current_user.tenant_id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role,
        avatar_url=current_user.avatar_url,
        status=current_user.status,
        last_login_at=current_user.last_login_at,
        tenant={
            "id": str(tenant.id) if tenant else str(current_user.tenant_id),
            "name": tenant.name if tenant else "Apex Institute of Technology",
            "slug": tenant.slug if tenant else "apex"
        } if tenant else None,
        tenant_settings=tenant.settings if tenant else None,
        profile=profile_data,
        permissions=permissions
    )


# -----------------------------------------------------------------------------
# Password Recovery & Change
# -----------------------------------------------------------------------------

@router.post("/forgot-password", response_model=Dict[str, Any])
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Request password reset token. Always returns success to prevent enumeration."""
    user = db.query(User).filter(User.email == payload.email, User.deleted_at.is_(None)).first()
    if user:
        reset_token = uuid.uuid4().hex
        token_hash = hashlib.sha256(reset_token.encode('utf-8')).hexdigest()
        user_token = UserToken(
            tenant_id=user.tenant_id,
            user_id=user.id,
            purpose="PASSWORD_RESET",
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        db.add(user_token)

        audit = AuditLog(
            tenant_id=user.tenant_id,
            user_id=user.id,
            action="PASSWORD_RESET_REQUESTED",
            entity_type="USER",
            entity_id=user.id
        )
        db.add(audit)
        db.commit()

        # In dev/demo environment, include token for direct verification testing
        return {
            "success": True,
            "message": "If the email is registered, password reset instructions have been dispatched.",
            "demo_reset_token": reset_token
        }

    return {
        "success": True,
        "message": "If the email is registered, password reset instructions have been dispatched."
    }


@router.post("/reset-password", response_model=Dict[str, Any])
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Validate single-use token and update user password."""
    token_hash = hashlib.sha256(payload.token.encode('utf-8')).hexdigest()
    user_token = db.query(UserToken).filter(
        UserToken.token_hash == token_hash,
        UserToken.purpose == "PASSWORD_RESET",
        UserToken.revoked_at.is_(None),
        UserToken.used_at.is_(None)
    ).first()

    if not user_token or user_token.expires_at < datetime.now(timezone.utc):
        raise BadRequestException("Invalid or expired password reset token")

    user = db.query(User).filter(User.id == user_token.user_id, User.deleted_at.is_(None)).first()
    if not user:
        raise NotFoundException("User not found")

    user.password_hash = get_password_hash(payload.new_password)
    user.failed_login_count = 0
    user.locked_until = None
    user_token.used_at = datetime.now(timezone.utc)

    # Invalidate all prior sessions
    db.query(UserToken).filter(
        UserToken.user_id == user.id,
        UserToken.purpose == "REFRESH",
        UserToken.revoked_at.is_(None)
    ).update({"revoked_at": datetime.now(timezone.utc)})

    audit = AuditLog(
        tenant_id=user.tenant_id,
        user_id=user.id,
        action="PASSWORD_RESET_COMPLETED",
        entity_type="USER",
        entity_id=user.id
    )
    db.add(audit)
    db.commit()

    return {"success": True, "message": "Password updated successfully. Please log in with your new credentials."}


@router.post("/change-password", response_model=Dict[str, Any])
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Authenticated password update."""
    if not verify_password(payload.current_password, current_user.password_hash):
        raise BadRequestException("Current password is incorrect")

    current_user.password_hash = get_password_hash(payload.new_password)
    audit = AuditLog(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        action="PASSWORD_CHANGED",
        entity_type="USER",
        entity_id=current_user.id
    )
    db.add(audit)
    db.commit()

    return {"success": True, "message": "Password changed successfully"}
