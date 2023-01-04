from typing import Dict, List

from pydantic import BaseModel, PositiveInt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.session import with_session
from app.models import Base


class BaseRepository:
    model_cls: Base

    @with_session
    async def search_items(
        self, search_data: Dict, session: AsyncSession = None
    ) -> List[Base]:
        qs = select(self.model_cls)
        for k, v in search_data.items():
            qs = qs.where(getattr(self.model_cls, k) == v)
        res = await session.execute(qs.order_by(self.model_cls.id))
        return res.scalars().all()

    @with_session
    async def get_by_id(
        self, item_id: PositiveInt, session: AsyncSession = None
    ) -> Base:
        res = await session.execute(select(self.model_cls).filter_by(id=item_id))
        return res.scalars().first()

    @with_session
    async def create_item(
        self, create_data: BaseModel, session: AsyncSession = None
    ) -> Base:
        new_item = self.model_cls(**create_data.dict())
        session.add(new_item)
        return new_item
