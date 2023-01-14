from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings


class ApplicationFactory:
    def __call__(self) -> FastAPI:
        application = FastAPI(
            title=settings.PROJECT_NAME,
            debug=settings.DEBUG,
            root_path=settings.ROOT_URL,
            openapi_url=settings.OPENAPI_URL,
            docs_url=None if settings.DISABLE_DOCS else settings.DOCS_URL,
        )
        application.include_router(router)
        return application


app_factory = ApplicationFactory()
