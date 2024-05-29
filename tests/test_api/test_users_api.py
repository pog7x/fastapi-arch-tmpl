import pytest
from httpx import AsyncClient

from tests.factories import UserFactory


class TestUserAPI:
    factory = UserFactory()
    api_path = "/users/"

    @pytest.mark.asyncio
    async def test_search_users(self, http_client: AsyncClient):
        expected_size = 15
        obj_dict = self.factory.build().model_dump(exclude={"address", "employment"})
        await self.factory.create_batch_async(size=expected_size, **obj_dict)
        await self.factory.create_batch_async(size=expected_size)
        resp = await http_client.get(self.api_path, params={**obj_dict})
        assert resp.is_success
        assert len(resp.json().get("result")) == expected_size

    @pytest.mark.asyncio
    async def test_get_user(self, http_client: AsyncClient):
        obj_dict = self.factory.build().model_dump()
        obj = await self.factory.create_async(**obj_dict)

        resp = await http_client.get(f"{self.api_path}{obj.id}")
        assert resp.is_success
        assert resp.json().get("result") == obj.model_dump(mode="json")

    @pytest.mark.asyncio
    async def test_create_user(self, http_client: AsyncClient):
        obj_dict = self.factory.build().model_dump(mode="json")

        resp = await http_client.post(self.api_path, json=obj_dict)
        assert resp.is_success
        result = resp.json().get("result")
        assert all(result[field] == value for field, value in obj_dict.items())

    @pytest.mark.asyncio
    async def test_delete_user(self, http_client: AsyncClient):
        obj_dict = self.factory.build().model_dump()
        obj = await self.factory.create_async(**obj_dict)

        resp = await http_client.delete(f"{self.api_path}{obj.id}")
        assert resp.is_success

        resp = await http_client.get(f"{self.api_path}{obj.id}")
        assert resp.is_success
        assert resp.json().get("result") is None

    @pytest.mark.asyncio
    async def test_update_user(self, http_client: AsyncClient):
        obj_dict = self.factory.build().model_dump()
        obj = await self.factory.create_async(**obj_dict)
        update_obj_dict = self.factory.build().model_dump(mode="json")

        resp = await http_client.get(f"{self.api_path}{obj.id}")
        assert resp.is_success
        assert resp.json().get("result") == obj.model_dump(mode="json")

        resp = await http_client.put(f"{self.api_path}{obj.id}", json=update_obj_dict)
        assert resp.is_success

        resp = await http_client.get(f"{self.api_path}{obj.id}")
        assert resp.is_success
        result = resp.json().get("result")
        assert all(result[field] == value for field, value in update_obj_dict.items())
