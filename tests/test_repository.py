import pytest
from tests.factories import UserFactory, ItemFactory
from app.repository.user_repository import UserRepository


@pytest.mark.asyncio
async def test_user_repository():
    c = await UserFactory()
    p = await ItemFactory(owner=c)
    p1 = await ItemFactory(owner=c)

    get_u = await UserRepository().get_by_id(item_id=c.id, join_related=["items"])
    assert get_u.name == c.name
    assert len(get_u.items) == 2
    for i in get_u.items:
        assert i.title in [p.title, p1.title]
