from fastapi import APIRouter

from app.api.client import router as client_router
from app.api.client_parking import router as client_parking_router
from app.api.parking import router as parking_router

router = APIRouter()

router.include_router(router=client_router, prefix="/clients")
router.include_router(router=parking_router, prefix="/parkings")
router.include_router(router=client_parking_router, prefix="/client_parking")
