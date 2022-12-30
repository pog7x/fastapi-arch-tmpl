from typing import List, Optional

from fastapi import APIRouter
from pydantic import PositiveInt, constr

from app import domain
from app.core.session import async_session
from app.models import Client
from app.repository.client_repository import ClientRepository

router = APIRouter(prefix="/clients")

client_repo = ClientRepository(session_maker=async_session)


class APIClientModel(domain.ClientModel):
    name: constr(min_length=2, max_length=50)
    surname: constr(min_length=2, max_length=50)


@router.get("/", response_model=List[domain.ClientModel])
async def search_clients(name: Optional[str] = None, surname: Optional[str] = None):
    return await client_repo.search_items(
        domain.ClientModel(name=name, surname=surname).dict(exclude_none=True),
    )


@router.post("/", response_model=domain.ClientModel)
async def create_client(client: APIClientModel) -> Client:
    return await client_repo.create_item(create_data=client)


@router.get("/{client_id}", response_model=domain.ClientModel)
async def get_client(client_id: PositiveInt) -> Client:
    return await client_repo.get_by_id(item_id=client_id)
