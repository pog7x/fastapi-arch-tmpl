import pytest

from app.models import User
from app.repository.user_repository import UserRepository
from tests.factories import UserFactory


class TestUserRepository:
    repo = UserRepository()
    factory = UserFactory()
    model_cls = User

    @pytest.mark.asyncio
    async def test_search_objects(self):
        expected_size = 15
        obj_dict = self.factory.build().model_dump(
            exclude_none=True, exclude={"address", "employment"}
        )

        await self.factory.create_batch_async(size=expected_size, **obj_dict)

        result = await self.repo.search_objects(obj_dict)

        assert len(result) == expected_size

    @pytest.mark.asyncio
    async def test_get_by_id(self):
        obj_dict = self.factory.build().model_dump()

        obj = await self.factory.create_async(**obj_dict)

        result = await self.repo.get_by_id(item_id=obj.id)

        assert result.model_dump(exclude={"id"}) == obj_dict

    @pytest.mark.asyncio
    async def test_create_object(self):
        obj_model: self.model_cls = self.factory.build()

        obj = await self.repo.create_object(obj_model)

        result = await self.repo.get_by_id(obj.id)

        assert result.model_dump(exclude={"id"}) == obj_model.model_dump()

    @pytest.mark.asyncio
    async def test_update_object(self):
        obj_dict = self.factory.build().model_dump()
        update_dict = self.factory.build().model_dump()
        update_model = self.factory.build()

        obj = await self.factory.create_async(**obj_dict)
        assert obj.model_dump(exclude={"id"}) == obj_dict

        result = await self.repo.update_object(obj, update_dict)
        assert result.model_dump(exclude={"id"}) == update_dict

        result = await self.repo.update_object(obj, update_model)
        assert result.model_dump(exclude={"id"}) == update_model.model_dump()

    @pytest.mark.asyncio
    async def test_delete_by_id(self):
        obj_dict = self.factory.build().model_dump()

        obj = await self.factory.create_async(**obj_dict)

        result = await self.repo.get_by_id(item_id=obj.id)
        assert result.model_dump(exclude={"id"}) == obj_dict

        await self.repo.delete_by_id(item_id=obj.id)

        assert await self.repo.get_by_id(item_id=obj.id) is None
