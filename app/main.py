import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings
from app.core.exceptions import AppException
from app.api.api_v1 import api_v1_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("nexora")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.PROJECT_NAME} in {settings.ENVIRONMENT} mode...")
    try:
        from app.database import engine, Base, SessionLocal
        import app.models  # register all SQLAlchemy models
        logger.info("Verifying database schema...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema verified.")

        # Ensure default tenant and essential demo accounts exist
        from app.models.platform import Tenant, User
        from app.core.security import get_password_hash
        import uuid
        db = SessionLocal()
        try:
            tenant_count = db.query(Tenant).count()
            if tenant_count == 0:
                logger.info("Empty database detected. Auto-seeding default tenant and demo accounts...")
                default_tenant = Tenant(
                    id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
                    name="Apex Institute of Technology",
                    slug="apex",
                    status="ACTIVE",
                    settings={
                        "domain": "apex.edu",
                        "logo_url": "/assets/nexora-logo-mark.png",
                        "grading_scale": "standard_gpa_4",
                        "primary_color": "#0ea5e9"
                    }
                )
                db.add(default_tenant)
                db.flush()

                users_to_seed = [
                    User(
                        id=uuid.UUID("11111111-1111-1111-1111-000000000001"),
                        tenant_id=default_tenant.id,
                        email="sanjudeepu.153@gmail.com",
                        first_name="Sanjay",
                        last_name="H S",
                        role="STUDENT",
                        password_hash=get_password_hash("sanju$123"),
                        status="ACTIVE"
                    ),
                    User(
                        id=uuid.UUID("11111111-1111-1111-1111-000000000002"),
                        tenant_id=default_tenant.id,
                        email="admin@apex.edu",
                        first_name="Dr. Rajesh",
                        last_name="Sharma",
                        role="ADMIN",
                        password_hash=get_password_hash("Password123!"),
                        status="ACTIVE"
                    ),
                    User(
                        id=uuid.UUID("11111111-1111-1111-1111-000000000003"),
                        tenant_id=default_tenant.id,
                        email="prof.priya@apex.edu",
                        first_name="Dr. Priya",
                        last_name="Nair",
                        role="FACULTY",
                        password_hash=get_password_hash("Password123!"),
                        status="ACTIVE"
                    ),
                    User(
                        id=uuid.UUID("2acee541-1735-4d62-ad94-602130299b4f"),
                        tenant_id=default_tenant.id,
                        email="dean.engineering@apex.edu",
                        first_name="Dr. Arvind",
                        last_name="Swaminathan",
                        role="DEAN",
                        password_hash=get_password_hash("Password123!"),
                        status="ACTIVE"
                    ),
                ]
                db.add_all(users_to_seed)
                db.commit()
                logger.info("Auto-seeded default tenant and 4 demo accounts successfully.")
        except Exception as seed_err:
            db.rollback()
            logger.warning(f"Auto-seed skipped or deferred: {seed_err}")
        finally:
            db.close()
    except Exception as db_err:
        logger.warning(f"Database schema auto-check failed: {db_err}")
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME}...")


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=(
            "Centralized, role-aware academic operations platform for administrators, faculty, and students — "
            "built around transparent workflows and real-time institutional intelligence.\n\n"
            "Strictly conforms to project_requirements.md, database_architecture.md, and api_spec.md."
        ),
        version="1.0.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
        lifespan=lifespan
    )

    # -------------------------------------------------------------------------
    # CORS Middleware (supports local dev and remote cloud frontend origins)
    # -------------------------------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_origin_regex=r"^https?://.*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -------------------------------------------------------------------------
    # Security & Anti-Caching Headers Middleware
    # -------------------------------------------------------------------------
    @app.middleware("http")
    async def security_and_cache_control_middleware(request: Request, call_next):
        response = await call_next(request)
        
        # Enforce strict anti-caching on all API routes so browsers never cache protected responses
        if request.url.path.startswith(settings.API_V1_STR) or request.url.path.startswith("/auth"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"

        # Defense-in-depth security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response

    # -------------------------------------------------------------------------
    # Exception Handlers
    # -------------------------------------------------------------------------
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.error_code,
                    "message": exc.detail,
                    "details": exc.extra
                }
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid request parameters or payload",
                    "details": exc.errors()
                }
            }
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        logger.error(f"Database error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": "An unexpected database operation error occurred",
                    "details": str(exc)
                }
            }
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled server error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "Internal server error occurred",
                    "details": str(exc) if settings.DEBUG else None
                }
            }
        )

    # -------------------------------------------------------------------------
    # Health check & Core routes
    # -------------------------------------------------------------------------
    @app.get("/health", tags=["System Health"])
    def health_check():
        return {
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
            "version": "1.0.0"
        }

    @app.get("/health/db", tags=["System Health"])
    def db_health_check():
        from sqlalchemy import text
        from app.database import engine
        try:
            with engine.connect() as conn:
                table_cnt = conn.execute(text("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'")).scalar()
                tenants_cnt = 0
                try:
                    tenants_cnt = conn.execute(text("SELECT count(*) FROM tenants")).scalar()
                except Exception:
                    pass
                return {
                    "database_connected": True,
                    "public_tables_count": table_cnt,
                    "tenants_count": tenants_cnt,
                    "db_host": engine.url.host,
                    "db_name": engine.url.database,
                }
        except Exception as e:
            return {
                "database_connected": False,
                "error": str(e),
                "db_host": getattr(engine.url, 'host', 'unknown') if hasattr(engine, 'url') else 'unknown',
            }

    @app.get("/", tags=["Root"])
    def root():
        return {
            "project": settings.PROJECT_NAME,
            "version": "1.0.0",
            "docs": f"{settings.API_V1_STR}/docs",
            "api_v1": settings.API_V1_STR
        }

    # -------------------------------------------------------------------------
    # Mount Modular Routers
    # -------------------------------------------------------------------------
    app.include_router(api_v1_router, prefix=settings.API_V1_STR)

    return app


app = create_application()
