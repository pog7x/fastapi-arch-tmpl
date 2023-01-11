import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, PostgresDsn, validator


class Settings(BaseSettings):
    DEBUG: bool = False
    AUTO_RELOAD: bool = False

    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 5555

    PROJECT_NAME: str
    ROOT_URL: str = ""
    SENTRY_DSN: Optional[HttpUrl] = None

    DISABLE_DOCS: bool = False
    OPENAPI_URL: str = "/openapi.json"
    DOCS_URL: str = "/docs"

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str
    POSTGRES_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("POSTGRES_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_HOST"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB')}",
        )

    class Config:
        case_sensitive = True


settings = Settings()
