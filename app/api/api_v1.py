from fastapi import APIRouter
from app.api.auth import router as auth_router, tenants_router
from app.api.admin import router as admin_router
from app.api.faculty import router as faculty_router
from app.api.student import router as student_router
from app.api.dean import router as dean_router
from app.api.shared import router as shared_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router)
api_v1_router.include_router(tenants_router)
api_v1_router.include_router(admin_router)
api_v1_router.include_router(faculty_router)
api_v1_router.include_router(dean_router)
api_v1_router.include_router(student_router)
api_v1_router.include_router(shared_router)
