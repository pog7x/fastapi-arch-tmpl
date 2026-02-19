import asyncio
import logging
from http import HTTPStatus
from json import JSONDecodeError
from typing import IO, Any, Dict, Iterable, Optional, Tuple

from httpx import USE_CLIENT_DEFAULT, AsyncClient, AsyncHTTPTransport, Response
from pydantic import ValidationError

logger = logging.getLogger(__name__)

PrimitiveData = str | int | float | bool
FileContent = IO[bytes] | bytes
QueryParams = (
    Optional[Dict[str, PrimitiveData]] | Optional[Iterable[Tuple[str, PrimitiveData]]]
)


class BaseAsyncHttpClient:
    _client_name = "BaseAsyncHttpClient"

    def __init__(
        self,
        base_url: str,
        timeout: float = 5.0,
        retries: int = 3,
        retry_delay: float = 0.2,
        token: Optional[str] = None,
        auth_login: Optional[str] = None,
        auth_pass: Optional[str] = None,
    ):
        self._base_url: str = base_url
        self._token: str = token
        self._timeout: float = timeout
        self._retries: int = retries
        self._retry_delay: float = retry_delay
        self._auth_log: str = auth_login
        self._auth_pass: str = auth_pass
        self._headers: Optional[Dict[str, str]] = None

    async def base_request(
        self,
        url: str,
        method: str,
        endpoint: str,
        params: Optional[QueryParams] = None,
        json: Optional[Any] = None,
        content: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        files: Optional[Dict[str, FileContent]] = None,
        skip_error_statuses: Iterable[int] = tuple(),
    ) -> Response:
        url_path = self._base_url + url
        logger.info(
            f"{self._client_name} request {method.upper()} {url_path}, params:"
            f" {params}, body: {json}"
        )
        auth = (
            (self._auth_log, self._auth_pass)
            if self._auth_log and self._auth_pass
            else USE_CLIENT_DEFAULT
        )

        try:
            resp = await self._send_base_request(
                method=method,
                url=url_path,
                params=params,
                json=json,
                content=content,
                headers=headers or self._headers,
                files=files,
                auth=auth,
            )
        except Exception as e:
            msg = (
                f"Unexpected server error {e} from {self._client_name}, endpoint"
                f" {endpoint}"
            )
            logger.exception(msg)
            raise HTTPServerException(exc=e, message=msg)

        if resp.is_error:
            logger.info(
                f"HTTP response {method.upper()} {resp.status_code} {url}, {resp.text}"
            )
            self._handle_http_not_ok_status_code(
                resp=resp, skip_error_statuses=skip_error_statuses
            )

        return resp

    def parse_and_validate_response(self, target_cls: Any, response: Response) -> Any:
        try:
            raw_data = response.json()
        except JSONDecodeError as e:
            msg = (
                "Can't decode response from"
                f" {self._client_name}:{response.content.decode()}"
            )
            logger.info(msg)
            raise HTTPServerException(exc=e, message=msg)

        try:
            target = target_cls(**raw_data)
        except ValidationError as e:
            logger.info(
                f"Can't validate json response from {self._client_name}:{raw_data} - {e.json()}"
            )
            raise HTTPServerException(
                exc=e,
                message=(
                    f"Can't validate json response from {self._client_name}:{raw_data}"
                ),
            )

        return target

    async def _send_base_request(
        self,
        method: str,
        url: str,
        params: QueryParams = None,
        json: Optional[Any] = None,
        content: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        files: Optional[Dict[str, FileContent]] = None,
        auth: Tuple[str, str] = USE_CLIENT_DEFAULT,
    ) -> Response:
        resp = Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

        async with AsyncClient(
            transport=AsyncHTTPTransport(retries=self._retries),
            follow_redirects=True,
        ) as client:
            for retry in reversed(range(self._retries)):
                resp = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    content=content,
                    headers=headers,
                    timeout=self._timeout,
                    files=files,
                    auth=auth,
                )
                if not HTTPStatus(resp.status_code).is_server_error:
                    return resp

                if retry:
                    await asyncio.sleep(self._retry_delay)
                    continue

        return resp

    def _handle_http_not_ok_status_code(
        self, resp: Response, skip_error_statuses: Iterable
    ) -> None:
        resp_status_code = resp.status_code
        if (
            HTTPStatus(resp_status_code).is_client_error
            and resp_status_code not in skip_error_statuses
        ):
            msg = (
                f"Status code {resp_status_code} response from"
                f" {self._client_name}:{resp.content.decode()}"
            )
            logger.info(msg)
            raise HTTPClientException(code=resp_status_code, message=msg)

        if (
            HTTPStatus(resp_status_code).is_server_error
            and resp_status_code not in skip_error_statuses
        ):
            raise HTTPServerException(
                message=(
                    f"Unexpected server error from {self._client_name} with status code"
                    f" {resp_status_code}"
                )
            )


class BaseHTTPException(Exception):
    def __init__(self, exc: Optional[Exception] = None, message: Optional[str] = None):
        self.exc: Exception = exc
        self.message: str = message


class HTTPServerException(BaseHTTPException):
    pass


class HTTPClientException(BaseHTTPException):
    def __init__(
        self, code: int, exc: Optional[Exception] = None, message: Optional[str] = None
    ):
        super().__init__(exc=exc, message=message)
        self.code = code
