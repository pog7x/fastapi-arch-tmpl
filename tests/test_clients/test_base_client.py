import random

import pytest
import respx
from httpx import ConnectTimeout, Response

from app.clients.base import (
    BaseAsyncHttpClient,
    HTTPClientException,
    HTTPServerException,
)


@pytest.mark.fast
@respx.mock
async def test_base_client_unable_to_connect_to_server(base_url):
    mocked_route = respx.get(base_url + "/srv/v1/test").mock(side_effect=ConnectTimeout)
    client = BaseAsyncHttpClient(base_url=base_url)
    with pytest.raises(HTTPServerException):
        await client.base_request(
            url="/srv/v1/test",
            method="get",
            endpoint="test",
        )
    assert mocked_route.called


@pytest.mark.fast
@respx.mock
async def test_base_client_unexpected_exception(base_url):
    mocked_route = respx.get(base_url + "/srv/v1/test").mock(side_effect=Exception)
    client = BaseAsyncHttpClient(base_url=base_url)
    with pytest.raises(HTTPServerException):
        await client.base_request(
            url="/srv/v1/test",
            method="get",
            endpoint="test",
        )
    assert mocked_route.called


@pytest.mark.fast
@respx.mock
async def test_base_client_retries(base_url):
    retries = 3
    mocked_route = respx.get(base_url + "/srv/v1/test")
    mocked_route.side_effect = [
        *[Response(status_code=random.randint(500, 599))] * (retries - 1),
        Response(status_code=200),
    ]
    client = BaseAsyncHttpClient(base_url=base_url, retries=retries, retry_delay=0.0001)
    resp = await client.base_request(
        url="/srv/v1/test",
        method="get",
        endpoint="test",
    )
    assert mocked_route.called
    assert mocked_route.call_count == retries
    assert resp.status_code == 200


@pytest.mark.fast
@respx.mock
@pytest.mark.parametrize(
    "to_return,error",
    (
        (Response(status_code=400), HTTPClientException),
        (Response(status_code=400, json={"error": "test"}), HTTPClientException),
    ),
)
async def test_base_client_not_retries_for_client_http_errors(
    base_url, to_return, error
):
    mocked_route = respx.get(base_url + "/srv/v1/test").mock(return_value=to_return)
    retries = 3
    client = BaseAsyncHttpClient(base_url=base_url, retries=retries, retry_delay=0.0001)
    with pytest.raises(error) as e:
        await client.base_request(
            url="/srv/v1/test",
            method="get",
            endpoint="test",
        )
    assert mocked_route.called
    assert mocked_route.call_count == 1
    assert e.value.code == 400
