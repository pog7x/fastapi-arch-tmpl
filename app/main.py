from logging.config import dictConfig

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from starlette.types import ASGIApp

from app.api.routes import router
from app.core.config import settings
from app.core.exceptions_handlers import (
    http_exception_handler,
    http_internal_error_handler,
    request_validation_exception_handler,
)
from app.core.logger import get_log_config


class ApplicationFactory:
    def __call__(self) -> ASGIApp:
        dictConfig(get_log_config(settings.DEBUG))
        application = FastAPI(
            title=settings.PROJECT_NAME,
            version=settings.PROJECT_VERSION,
            debug=settings.DEBUG,
            root_path=settings.ROOT_URL,
            openapi_url=settings.OPENAPI_URL,
            docs_url=None if settings.DISABLE_DOCS else settings.DOCS_URL,
        )
        application.include_router(router)
        self._init_exception_handlers(app=application)
        return application

    @staticmethod
    def _init_exception_handlers(app: FastAPI) -> None:
        app.add_exception_handler(
            HTTP_500_INTERNAL_SERVER_ERROR, http_internal_error_handler
        )
        app.add_exception_handler(StarletteHTTPException, http_exception_handler)
        app.add_exception_handler(
            RequestValidationError, request_validation_exception_handler
        )


app_factory = ApplicationFactory()
