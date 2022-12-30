from typing import Dict, List

from pydantic import BaseModel, PositiveInt
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Base
from app.core.session import with_session

class BaseRepository:
    model_cls: Base

    def __init__(self, session_maker: sessionmaker) -> None:
        self._session_maker = session_maker

    @with_session
    async def search_items(self, search_data: Dict, session: AsyncSession = None) -> List[Base]:
        qs = select(self.model_cls)
        for k, v in search_data.items():
            qs = qs.where(getattr(self.model_cls, k) == v)
        res = await session.execute(qs.order_by(self.model_cls.id))
        return res.scalars().all()

    @with_session
    async def get_by_id(self, item_id: PositiveInt, session: AsyncSession = None) -> Base:
        res = await session.execute(
            select(self.model_cls, self.model_cls.id == item_id)
        )
        return res.scalars().first()

    @with_session
    async def create_item(self, create_data: BaseModel, session: AsyncSession = None) -> Base:
        new_item = self.model_cls(**create_data.dict())
        session.add(new_item)
        return new_item
