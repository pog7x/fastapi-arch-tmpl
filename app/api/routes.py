from fastapi import APIRouter

from app.api.items import router as items_router
from app.api.users import router as users_router

router = APIRouter()

router.include_router(router=users_router, prefix="/users")
router.include_router(router=items_router, prefix="/items")
