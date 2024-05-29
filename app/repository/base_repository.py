from typing import Any, Dict, Iterable, List, Optional, TypeVar, Union

from pydantic import BaseModel, NonNegativeInt, PositiveInt
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.core.session import with_session
from app.models import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository:
    model_cls: ModelType

    def __init__(self):
        self._inspect_model = inspect(self.model_cls)
        self._model_fields = [c.key for c in self._inspect_model.mapper.column_attrs]
        self._relationships = [r.key for r in self._inspect_model.relationships]

    @with_session
    async def search_objects(
        self,
        search_data: Dict,
        limit: PositiveInt = 20,
        offset: NonNegativeInt = 0,
        join_related: Iterable[str] = (),
        session: Optional[AsyncSession] = None,
    ) -> List[ModelType]:
        qs = select(self.model_cls)

        for k, v in search_data.items():
            if k in self._model_fields:
                qs = qs.where(getattr(self.model_cls, k) == v)

        for jr in join_related:
            if jr in self._relationships:
                qs = qs.options(joinedload(getattr(self.model_cls, jr)))

        res = await session.execute(
            qs.order_by(self.model_cls.id).limit(limit).offset(offset)
        )

        if join_related:
            return res.scalars().unique().all()

        return res.scalars().all()

    @with_session
    async def get_by_id(
        self,
        item_id: PositiveInt,
        join_related: Iterable[str] = (),
        session: Optional[AsyncSession] = None,
    ) -> ModelType:
        qs = select(self.model_cls).filter_by(id=item_id)

        for jr in join_related:
            if jr in self._relationships:
                qs = qs.options(joinedload(getattr(self.model_cls, jr)))

        res = await session.execute(qs)
        return res.scalars().first()

    @with_session
    async def create_object(
        self,
        create_data: CreateSchemaType,
        session: Optional[AsyncSession] = None,
    ) -> ModelType:
        new_item = self.model_cls(**create_data.model_dump())
        session.add(new_item)
        return new_item

    @with_session
    async def update_object(
        self,
        db_item: ModelType,
        update_data: Union[UpdateSchemaType, Dict[str, Any]],
        session: Optional[AsyncSession] = None,
    ) -> ModelType:
        if isinstance(update_data, dict):
            obj_in = update_data
        else:
            obj_in = update_data.model_dump(exclude_unset=True)

        for field in obj_in:
            if field in self._model_fields:
                setattr(db_item, field, obj_in[field])

        session.add(db_item)
        return db_item

    @with_session
    async def delete_by_id(
        self,
        item_id: PositiveInt,
        session: Optional[AsyncSession] = None,
    ) -> None:
        item = await session.get(self.model_cls, item_id)
        return await session.delete(item) if item else None
