from typing import List, Optional

from fastapi import APIRouter
from pydantic import PositiveInt, constr

from app import domain
from app.core.session import async_session
from app.models import Client
from app.repository.client_repository import ClientRepository

session = async_session()

router = APIRouter()


class APIClientModel(domain.ClientModel):
    name: constr(min_length=2, max_length=50)
    surname: constr(min_length=2, max_length=50)


@router.get("/", response_model=List[domain.ClientModel])
async def search_clients(name: Optional[str] = None, surname: Optional[str] = None):
    return await ClientRepository().search_items(
        domain.ClientModel(name=name, surname=surname).dict(exclude_none=True),
    )


@router.post("/", response_model=domain.ClientModel)
async def create_client(client: APIClientModel) -> Client:
    return await ClientRepository().create_item(create_data=client)


@router.get("/{client_id}", response_model=domain.ClientModel)
async def get_client(client_id: PositiveInt) -> Client:
    return await ClientRepository().get_by_id(item_id=client_id)


@router.delete("/{client_id}", response_model=domain.ClientModel)
async def get_client(client_id: PositiveInt) -> Client:
    return await ClientRepository().delete_by_id(item_id=client_id)


@router.put("/{client_id}", response_model=domain.ClientModel)
async def get_client(client_id: PositiveInt, client: APIClientModel) -> Client:
    item = await ClientRepository().get_by_id(item_id=client_id)
    return await ClientRepository().update_item(db_item=item, update_data=client)
