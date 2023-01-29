from fastapi import APIRouter

from app.api.coffee import router as coffee_router
from app.api.users import router as users_router

router = APIRouter()

router.include_router(router=users_router, prefix="/users", tags=["users"])
router.include_router(router=coffee_router, prefix="/coffee", tags=["coffee"])
