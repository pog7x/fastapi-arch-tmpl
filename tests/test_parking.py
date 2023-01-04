import pytest

from tests.factories import ClientFactory, ParkingFactory


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "url",
    (
        "/clients",
        "/clients?name=Test",
    ),
)
async def test_get_user_empty_ok(client, url):
    resp = await client.get(url=url)
    assert resp.status_code == 200


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "body, expected_code",
    (
        (
            {
                "name": "Test",
                "surname": "Testing",
                "credit_card": "2363272637623",
                "car_number": "232GUS8910",
            },
            200,
        ),
        (
            {
                "name": "Testing",
                "surname": "Testing",
                "credit_card": "2363272637623",
                "car_number": "232GUS81221212910",
            },
            422,
        ),
        (
            {
                "name": "",
                "surname": "Testing",
                "credit_card": "2363272637623",
                "car_number": "232GUS8910",
            },
            422,
        ),
        (
            {
                "name": "Test",
                "surname": "",
                "credit_card": "2363272637623",
                "car_number": "232GUS8910",
            },
            422,
        ),
    ),
)
async def test_create_client_response_codes(client, body, expected_code):
    resp = await client.post(
        url="/clients",
        json=body,
    )
    assert resp.status_code == expected_code
    if expected_code == 200:
        resp_body = resp.json()
        assert resp_body["id"] is not None
        for field in body:
            assert resp_body[field] == body[field]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "body, expected_code",
    (
        (
            {
                "address": "Москва, ул Тверская, д 20, кв 13",
                "opened": True,
                "count_places": 100,
                "count_available_places": 1,
            },
            200,
        ),
        (
            {
                "address": "Москва, ул Тверская, д 20, кв 13",
                "opened": None,
                "count_places": 100,
                "count_available_places": 1,
            },
            422,
        ),
        (
            {
                "address": "Москва, ул Тверская, д 20, кв 13",
                "opened": True,
                "count_places": 0,
                "count_available_places": 1,
            },
            422,
        ),
        (
            {
                "address": "Москва, ул Тверская, д 20, кв 13",
                "opened": True,
                "count_places": 50,
                "count_available_places": 100,
            },
            422,
        ),
    ),
)
async def test_create_parking_response_codes(client, body, expected_code):
    resp = await client.post(
        url="/parkings",
        json=body,
    )
    assert resp.status_code == expected_code
    if expected_code == 200:
        resp_body = resp.json()
        assert resp_body["id"] is not None
        for field in body:
            assert resp_body[field] == body[field]


@pytest.mark.parking
@pytest.mark.asyncio
async def test_create_client_parking_ok(client):
    c = await ClientFactory()
    p = await ParkingFactory()

    p_available_places_before = p.count_available_places
    resp = await client.post(
        url="/client_parking",
        json={
            "client_id": c.id,
            "parking_id": p.id,
        },
    )
    assert resp.status_code == 200
    assert p.count_available_places == p_available_places_before - 1

    resp_body = resp.json()
    assert resp_body["id"] is not None
    assert resp_body["client_id"] == c.id
    assert resp_body["parking_id"] == p.id
    assert resp_body["time_in"] is not None


@pytest.mark.parking
@pytest.mark.asyncio
async def test_create_and_delete_client_parking_flow(session, client):
    c = await ClientFactory()
    p = await ParkingFactory()

    p_available_places_before = p.count_available_places
    resp = await client.post(
        url="/client_parking",
        json={
            "client_id": c.id,
            "parking_id": p.id,
        },
    )
    assert resp.status_code == 200
    assert p.count_available_places == p_available_places_before - 1

    resp_body = resp.json()
    new_client_parking = resp_body["id"]
    assert new_client_parking is not None
    assert resp_body["client_id"] == c.id
    assert resp_body["parking_id"] == p.id
    assert resp_body["time_in"] is not None

    resp = await client.request(
        url="/client_parking",
        json={
            "client_id": c.id,
            "parking_id": p.id,
        },
        method="DELETE",
    )
    assert resp.status_code == 200
    assert p.count_available_places == p_available_places_before

    resp_body = resp.json()
    assert resp_body["id"] == new_client_parking
    assert resp_body["client_id"] == c.id
    assert resp_body["parking_id"] == p.id
    assert resp_body["time_in"] is not None
    assert resp_body["time_out"] is not None
