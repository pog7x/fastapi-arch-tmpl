from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings


def get_application() -> FastAPI:
    application = FastAPI(title=settings.PROJECT_NAME)
    application.include_router(router)
    return application


app = get_application()
