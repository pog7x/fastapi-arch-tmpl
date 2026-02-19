import random
from http import HTTPMethod, HTTPStatus

import pytest
import respx
from httpx import ConnectTimeout, Response

from app.clients.base import (
    BaseAsyncHttpClient,
    HTTPClientException,
    HTTPServerException,
)


@pytest.mark.fast
async def test_base_client_unable_to_connect_to_server(base_url):
    url = "/srv/v1/test"
    async with respx.mock(base_url=base_url, using="httpx") as respx_mock:
        mocked_route = respx_mock.get(url).mock(side_effect=ConnectTimeout)
        client = BaseAsyncHttpClient(base_url=base_url)
        with pytest.raises(HTTPServerException):
            await client.base_request(
                url=url,
                method=HTTPMethod.GET,
                endpoint="test",
            )
        assert mocked_route.called


@pytest.mark.fast
async def test_base_client_unexpected_exception(base_url):
    url = "/srv/v1/test"
    async with respx.mock(base_url=base_url, using="httpx") as respx_mock:
        mocked_route = respx_mock.get(url).mock(side_effect=Exception)
        client = BaseAsyncHttpClient(base_url=base_url)
        with pytest.raises(HTTPServerException):
            await client.base_request(
                url=url,
                method=HTTPMethod.GET,
                endpoint="test",
            )
        assert mocked_route.called


@pytest.mark.fast
async def test_base_client_retries(base_url):
    retries = random.randint(5, 15)
    url = "/srv/v1/test"

    def random_server_error():
        return random.choice(
            (HTTPStatus.INTERNAL_SERVER_ERROR, HTTPStatus.SERVICE_UNAVAILABLE)
        )

    async with respx.mock(base_url=base_url, using="httpx") as respx_mock:
        mocked_route = respx_mock.get(url)
        mocked_route.side_effect = [
            *[Response(status_code=random_server_error())] * (retries - 1),
            Response(status_code=HTTPStatus.OK),
        ]
        client = BaseAsyncHttpClient(
            base_url=base_url, retries=retries, retry_delay=0.0001
        )
        resp = await client.base_request(
            url=url,
            method=HTTPMethod.GET,
            endpoint="test",
        )
        assert mocked_route.called
        assert mocked_route.call_count == retries
        assert resp.status_code == HTTPStatus.OK


@pytest.mark.fast
@pytest.mark.parametrize(
    "to_return,error",
    (
        (Response(HTTPStatus.BAD_REQUEST), HTTPClientException),
        (Response(HTTPStatus.BAD_REQUEST, json={"error": "test"}), HTTPClientException),
    ),
)
async def test_base_client_not_retries_for_client_http_errors(
    base_url, to_return, error
):
    retries = random.randint(5, 15)
    url = "/srv/v1/test"
    async with respx.mock(base_url=base_url, using="httpx") as respx_mock:
        mocked_route = respx_mock.get(url).mock(return_value=to_return)
        client = BaseAsyncHttpClient(
            base_url=base_url, retries=retries, retry_delay=0.0001
        )
        with pytest.raises(error) as err:
            await client.base_request(
                url=url,
                method=HTTPMethod.GET,
                endpoint="test",
            )
        assert mocked_route.called
        assert mocked_route.call_count == 1
        assert err.value.code == to_return.status_code
