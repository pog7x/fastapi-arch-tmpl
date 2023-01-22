from typing import List

from fastapi import APIRouter
from pydantic import PositiveInt

from app.models import Item
from app.repository.item_repository import ItemRepository
from app.schemas import ItemModel

router = APIRouter()


@router.post("/", response_model=ItemModel)
async def create_item(item: ItemModel) -> Item:
    return await ItemRepository().create_object(create_data=item)


@router.get("/", response_model=List[ItemModel])
async def search_items() -> List[Item]:
    return await ItemRepository().search_objects(
        ItemModel().dict(exclude_none=True),
        join_related=["owner"],
    )


@router.get("/{item_id}", response_model=ItemModel)
async def get_item(item_id: PositiveInt) -> Item:
    return await ItemRepository().get_by_id(item_id=item_id)


@router.delete("/{item_id}", response_model=ItemModel)
async def delete_item(item_id: PositiveInt) -> Item:
    return await ItemRepository().delete_by_id(item_id=item_id)


@router.put("/{item_id}", response_model=ItemModel)
async def update_item(item_id: PositiveInt, item: ItemModel) -> Item:
    obj = await ItemRepository().get_by_id(item_id=item_id)
    return await ItemRepository().update_object(db_item=obj, update_data=item)
