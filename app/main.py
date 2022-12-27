from typing import Callable

from fastapi import FastAPI

from app.routes import router


def get_application() -> FastAPI:
    application = FastAPI(title="Parking")

    application.include_router(router)
    return application


app = get_application()
