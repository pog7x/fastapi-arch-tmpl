import http
from typing import List

from fastapi import APIRouter, Body
from pydantic import PositiveInt
from starlette.responses import JSONResponse
from starlette.status import HTTP_404_NOT_FOUND

from app.core.base_response import BaseResponse
from app.models.user import User
from app.repository.user_repository import UserRepository

router = APIRouter()


@router.get("/", response_model=BaseResponse[List[User]])
async def search_users(
    first_name: str | None = None, last_name: str | None = None
) -> Body:
    result = await UserRepository().search_objects(
        User(first_name=first_name or None, last_name=last_name or None).model_dump(
            exclude_none=True
        ),
        join_related=["coffee"],
    )
    return BaseResponse.from_result(result=result).dict()


@router.post("/", response_model=BaseResponse[User])
async def create_user(user: User) -> Body:
    result = await UserRepository().create_object(create_data=user)
    return BaseResponse.from_result(result=result).dict()


@router.get("/{user_id}", response_model=BaseResponse[User])
async def get_user(user_id: PositiveInt) -> Body:
    result = await UserRepository().get_by_id(item_id=user_id, join_related=["coffee"])
    return BaseResponse.from_result(result=result).dict()


@router.delete("/{user_id}", response_model=BaseResponse)
async def delete_user(user_id: PositiveInt) -> Body:
    result = await UserRepository().delete_by_id(item_id=user_id)
    return BaseResponse.from_result(result=result).dict()


@router.put("/{user_id}", response_model=BaseResponse[User])
async def update_user(user_id: PositiveInt, user: User) -> Body:
    item = await UserRepository().get_by_id(item_id=user_id)
    if not item:
        return JSONResponse(
            content=BaseResponse.from_error_str(
                http.HTTPStatus(HTTP_404_NOT_FOUND).phrase
            ).dict(),
            status_code=HTTP_404_NOT_FOUND,
        )
    result = await UserRepository().update_object(db_item=item, update_data=user)
    return BaseResponse.from_result(result=result).dict()
