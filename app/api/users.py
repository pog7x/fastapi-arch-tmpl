from typing import List, Optional

from fastapi import APIRouter, Body
from pydantic import PositiveInt

from app.core.base_response import BaseResponse
from app.repository.user_repository import UserRepository
from app.schemas import UserModel, UserWithCoffeeModel

router = APIRouter()


@router.get("/", response_model=BaseResponse[List[UserWithCoffeeModel]])
async def search_users(
    name: Optional[str] = None, surname: Optional[str] = None
) -> Body:
    result = await UserRepository().search_objects(
        UserModel(name=name, surname=surname).dict(exclude_none=True),
        join_related=["coffee"],
    )
    return BaseResponse.from_result(result=result).dict()


@router.post("/", response_model=BaseResponse[UserModel])
async def create_user(user: UserModel) -> Body:
    result = await UserRepository().create_object(create_data=user)
    return BaseResponse.from_result(result=result).dict()


@router.get("/{user_id}", response_model=BaseResponse[UserWithCoffeeModel])
async def get_user(user_id: PositiveInt) -> Body:
    result = await UserRepository().get_by_id(item_id=user_id, join_related=["coffee"])
    return BaseResponse.from_result(result=result).dict()


@router.delete("/{user_id}", response_model=BaseResponse)
async def delete_user(user_id: PositiveInt) -> Body:
    result = await UserRepository().delete_by_id(item_id=user_id)
    return BaseResponse.from_result(result=result).dict()


@router.put("/{user_id}", response_model=BaseResponse[UserModel])
async def update_user(user_id: PositiveInt, user: UserModel) -> Body:
    item = await UserRepository().get_by_id(item_id=user_id)
    result = await UserRepository().update_object(db_item=item, update_data=user)
    return BaseResponse.from_result(result=result).dict()
