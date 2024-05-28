import pytest

from app.models import Coffee
from app.repository.coffee_repository import CoffeeRepository
from tests.factories import CoffeeFactory


class TestCoffeeRepository:
    repo = CoffeeRepository()
    factory = CoffeeFactory()
    model_cls = Coffee

    @pytest.mark.asyncio
    async def test_search_objects(self):
        expected_size = 15
        obj_dict = self.factory.build().model_dump()

        await self.factory.create_batch_async(size=expected_size, **obj_dict)

        result = await self.repo.search_objects(obj_dict)

        assert len(result) == expected_size

    @pytest.mark.asyncio
    async def test_get_by_id(self):
        obj_dict = self.factory.build().model_dump()
        obj = await self.factory.create_async(**obj_dict)

        result = await self.repo.get_by_id(item_id=obj.id)

        assert result.id == obj.id
        assert result == obj

    @pytest.mark.asyncio
    async def test_create_object(self):
        obj_model = self.factory.build()
        obj = await self.repo.create_object(obj_model)

        result = await self.repo.get_by_id(obj.id)

        assert result == obj

    @pytest.mark.asyncio
    async def test_update_object(self):
        obj_dict = self.factory.build().model_dump()
        update_dict = self.factory.build().model_dump()
        update_model = self.factory.build()
        obj = await self.factory.create_async(**obj_dict)

        upd = await self.repo.update_object(obj, update_dict)
        assert upd.model_dump(exclude={"id"}) == update_dict

        upd = await self.repo.update_object(upd, update_model)
        assert upd.model_dump(exclude={"id"}) == update_model.model_dump()

    @pytest.mark.asyncio
    async def test_delete_by_id(self):
        obj_dict = self.factory.build().model_dump()
        obj = await self.factory.create_async(**obj_dict)

        assert await self.repo.get_by_id(item_id=obj.id) == obj

        await self.repo.delete_by_id(item_id=obj.id)
        assert await self.repo.get_by_id(item_id=obj.id) is None
