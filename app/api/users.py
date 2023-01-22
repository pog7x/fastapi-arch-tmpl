from typing import List, Optional

from fastapi import APIRouter
from pydantic import PositiveInt

from app.models import User
from app.repository.user_repository import UserRepository
from app.schemas import UserModel, UserWithItemsModel

router = APIRouter()


@router.get("/", response_model=List[UserWithItemsModel])
async def search_users(
    name: Optional[str] = None, surname: Optional[str] = None
) -> List[User]:
    return await UserRepository().search_objects(
        UserModel(name=name, surname=surname).dict(exclude_none=True),
        join_related=["items"]
    )


@router.post("/", response_model=UserModel)
async def create_user(user: UserModel) -> User:
    return await UserRepository().create_object(create_data=user)


@router.get("/{user_id}", response_model=UserModel)
async def get_user(user_id: PositiveInt) -> User:
    return await UserRepository().get_by_id(item_id=user_id)


@router.delete("/{user_id}", response_model=UserModel)
async def delete_user(user_id: PositiveInt) -> User:
    return await UserRepository().delete_by_id(item_id=user_id)


@router.put("/{user_id}", response_model=UserModel)
async def update_user(user_id: PositiveInt, user: UserModel) -> User:
    obj = await UserRepository().get_by_id(item_id=user_id)
    return await UserRepository().update_object(db_item=obj, update_data=user)
