from typing import Any, Dict, List, TypeVar, Union

from pydantic import BaseModel, PositiveInt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import inspect
from app.core.session import with_session
from app.models import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository:
    model_cls: ModelType

    def __init__(self):
        self._column_attrs = [c.key for c in inspect(self.model_cls).mapper.column_attrs]

    @with_session
    async def search_items(
        self,
        search_data: Dict,
        session: AsyncSession = None,
    ) -> List[ModelType]:
        qs = select(self.model_cls)

        for k, v in search_data.items():
            if k in self._column_attrs:
                qs = qs.where(getattr(self.model_cls, k) == v)

        res = await session.execute(qs.order_by(self.model_cls.id))
        return res.scalars().all()

    @with_session
    async def get_by_id(
        self,
        item_id: PositiveInt,
        session: AsyncSession = None,
    ) -> ModelType:
        res = await session.execute(select(self.model_cls).filter_by(id=item_id))
        return res.scalars().first()

    @with_session
    async def create_item(
        self,
        create_data: BaseModel,
        session: AsyncSession = None,
    ) -> Base:
        new_item = self.model_cls(**create_data.dict())
        session.add(new_item)
        return new_item

    @with_session
    async def update_item(
        self,
        db_item: ModelType,
        update_data: Union[UpdateSchemaType, Dict[str, Any]],
        session: AsyncSession = None,
    ) -> ModelType:
        if isinstance(update_data, dict):
            obj_in = update_data
        else:
            obj_in = update_data.dict(exclude_unset=True)

        for field in obj_in:
            if field in self._column_attrs:
                setattr(db_item, field, obj_in[field])

        session.add(db_item)
        return db_item

    @with_session
    async def delete_by_id(
        self,
        item_id: PositiveInt,
        session: AsyncSession = None,
    ) -> None:
        item = await session.get(self.model_cls, item_id)
        return await session.delete(item) if item else None
