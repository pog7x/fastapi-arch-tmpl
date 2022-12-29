from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict
from app.models import Client
from pydantic import PositiveInt
from sqlalchemy.future import select
from typing import Optional, List


class ClientRepository:
    def __init__(self, session_maker: sessionmaker) -> None:
        self._session_maker = session_maker

    async def create_client(self, create_data: Dict) -> Client:
        new_client = Client(**create_data)
        async with self._session_maker.begin() as session:
            session.add(new_client)
            return new_client

    async def get_client(self, client_id: PositiveInt) -> Client:
        async with self._session_maker.begin() as session:
            res = await session.execute(select(Client).filter_by(id=client_id))
            return res.scalars().first()

    async def search_clients(self, name: Optional[str] = None, surname: Optional[str] = None) -> List[Client]:
        async with self._session_maker.begin() as session:
            qs = select(Client)
            if name:
                qs = qs.where(Client.name == name)
            if surname:
                qs = qs.where(Client.surname == surname)
            res = await session.execute(qs.order_by(Client.id))
            return res.scalars().all()