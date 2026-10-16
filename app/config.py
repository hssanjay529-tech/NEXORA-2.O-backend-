import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "NEXORA — College Management Portal"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    POSTGRES_USER: str = "nexora_admin"
    POSTGRES_PASSWORD: str = "nexora_password"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "nexora"
    DATABASE_URL: str = "postgresql+psycopg2://nexora_admin:nexora_password@localhost:5432/nexora"

    # Security & JWT
    SECRET_KEY: str = "nexora-insecure-secret-key-change-in-production-2026-secure-jwt"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Multi-Tenancy
    DEFAULT_TENANT_ID: str = "11111111-1111-1111-1111-111111111111"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
    ]

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_database_url(cls, v: str) -> str:
        if not v or not isinstance(v, str):
            return v
        cleaned = v.strip()
        # Normalize driver for SQLAlchemy + psycopg2
        if cleaned.startswith("postgres://"):
            cleaned = "postgresql+psycopg2://" + cleaned[len("postgres://"):]
        elif cleaned.startswith("postgresql://") and not cleaned.startswith("postgresql+psycopg2://"):
            cleaned = "postgresql+psycopg2://" + cleaned[len("postgresql://"):]
        # Append sslmode=require for remote cloud databases like Supabase if absent
        if ("pooler.supabase.com" in cleaned or "supabase.co" in cleaned) and "sslmode=" not in cleaned:
            sep = "&" if "?" in cleaned else "?"
            cleaned = f"{cleaned}{sep}sslmode=require"
        return cleaned

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
