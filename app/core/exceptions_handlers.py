import http

from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from app.core.base_response import BaseResponse


async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        BaseResponse.from_error_str(exc.detail).dict(),
        status_code=exc.status_code,
        headers=getattr(exc, "headers", None),
    )


async def http_internal_error_handler(*_) -> JSONResponse:
    content = BaseResponse.from_error_str(
        http.HTTPStatus(HTTP_500_INTERNAL_SERVER_ERROR).phrase
    ).dict()
    return JSONResponse(content, status_code=HTTP_500_INTERNAL_SERVER_ERROR)


async def request_validation_exception_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    content = BaseResponse(errors=jsonable_encoder(exc.errors())).dict()
    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content=content,
    )
