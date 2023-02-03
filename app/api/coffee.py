import http
from typing import List

from fastapi import APIRouter, Body
from pydantic import PositiveInt
from starlette.responses import JSONResponse
from starlette.status import HTTP_404_NOT_FOUND

from app.core.base_response import BaseResponse
from app.repository.coffee_repository import CoffeeRepository
from app.schemas import CoffeeModel, CoffeeWithUsersModel

router = APIRouter()


@router.post("/", response_model=BaseResponse[CoffeeModel])
async def create_coffee(coffee: CoffeeModel) -> Body:
    result = await CoffeeRepository().create_object(create_data=coffee)
    return BaseResponse.from_result(result=result).dict()


@router.get("/", response_model=BaseResponse[List[CoffeeWithUsersModel]])
async def search_coffee() -> Body:
    result = await CoffeeRepository().search_objects(
        CoffeeModel().dict(exclude_none=True),
        join_related=["users"],
    )
    return BaseResponse.from_result(result=result).dict()


@router.get("/{coffee_id}", response_model=BaseResponse[CoffeeWithUsersModel])
async def get_coffee(coffee_id: PositiveInt) -> Body:
    result = await CoffeeRepository().get_by_id(
        item_id=coffee_id, join_related=["users"]
    )
    return BaseResponse.from_result(result=result).dict()


@router.delete("/{coffee_id}", response_model=BaseResponse)
async def delete_coffee(coffee_id: PositiveInt) -> Body:
    result = await CoffeeRepository().delete_by_id(item_id=coffee_id)
    return BaseResponse.from_result(result=result).dict()


@router.put("/{coffee_id}", response_model=BaseResponse[CoffeeModel])
async def update_coffee(coffee_id: PositiveInt, coffee: CoffeeModel) -> Body:
    item = await CoffeeRepository().get_by_id(item_id=coffee_id)
    if not item:
        return JSONResponse(
            content=BaseResponse.from_error_str(
                http.HTTPStatus(HTTP_404_NOT_FOUND).phrase
            ).dict(),
            status_code=HTTP_404_NOT_FOUND,
        )
    result = await CoffeeRepository().update_object(db_item=item, update_data=coffee)
    return BaseResponse.from_result(result=result).dict()
