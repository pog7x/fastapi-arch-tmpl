from fastapi import APIRouter, FastAPI

from app.api.client import router as client_router
from app.api.client_parking import router as client_parking_router
from app.api.parking import router as parking_router


def get_application() -> FastAPI:
    application = FastAPI(title="Parking")
    router = APIRouter()
    router.include_router(client_router)
    router.include_router(parking_router)
    router.include_router(client_parking_router)
    application.include_router(router)
    return application


app = get_application()
