from pydantic import HttpUrl, PostgresDsn, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DEBUG: bool = False
    AUTO_RELOAD: bool = False

    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 5555

    PROJECT_NAME: str
    PROJECT_VERSION: str = "0.0.1"
    ROOT_URL: str = ""
    SENTRY_DSN: HttpUrl | None = None

    DISABLE_DOCS: bool = False
    OPENAPI_URL: str = "/openapi.json"
    DOCS_URL: str = "/docs"

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_DATABASE_URI: str | None = None

    RMQ_USER: str
    RMQ_PASSWORD: str
    RMQ_HOST: str
    RMQ_PORT: int
    RMQ_VHOST: str
    RMQ_EXCHANGE: str
    RMQ_ROUTING_KEY: str
    RMQ_QUEUE: str

    @field_validator("POSTGRES_DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> str:
        if isinstance(v, str):
            return v
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=info.data.get("POSTGRES_USER"),
                password=info.data.get("POSTGRES_PASSWORD"),
                host=info.data.get("POSTGRES_HOST"),
                port=info.data.get("POSTGRES_PORT"),
                path=info.data.get("POSTGRES_DB"),
            )
        )

    model_config = SettingsConfigDict(case_sensitive=True)


settings = Settings()
