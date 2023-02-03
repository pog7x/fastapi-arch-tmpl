import asyncio
from logging.config import dictConfig

import aio_pika
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from starlette.types import ASGIApp

from app.api.publish_consume_coffee import create_coffee_callback
from app.api.routes import router
from app.core.config import settings
from app.core.exceptions_handlers import (
    http_exception_handler,
    http_internal_error_handler,
    request_validation_exception_handler,
)
from app.core.logger import get_log_config
from app.rmq.consumer import Exchange2Consume, RMQConsumer
from app.rmq.publisher import RMQPublisher


def connect_rmq(app: FastAPI):
    async def start() -> None:
        await app.state.pub.start()
        asyncio.create_task(app.state.sub.start())

    return start


def disconnect_rmq(app: FastAPI):
    async def stop() -> None:
        await app.state.pub.stop()
        await app.state.sub.stop()

    return stop


class ApplicationFactory:
    def __call__(self) -> ASGIApp:
        dictConfig(get_log_config(settings.DEBUG))
        application = FastAPI(
            title=settings.PROJECT_NAME,
            version=settings.PROJECT_VERSION,
            debug=settings.DEBUG,
            root_path=settings.ROOT_URL,
            openapi_url=settings.OPENAPI_URL,
            docs_url=None if settings.DISABLE_DOCS else settings.DOCS_URL,
        )
        application.include_router(router)
        self._init_exception_handlers(app=application)

        pub = RMQPublisher(
            host=settings.RMQ_HOST,
            port=settings.RMQ_PORT,
            virtualhost=settings.RMQ_VHOST,
            login=settings.RMQ_USER,
            password=settings.RMQ_PASSWORD,
            exchange_name=settings.RMQ_EXCHANGE,
            exchange_type=aio_pika.ExchangeType.TOPIC,
        )

        sub = RMQConsumer(
            host=settings.RMQ_HOST,
            port=settings.RMQ_PORT,
            virtualhost=settings.RMQ_VHOST,
            login=settings.RMQ_USER,
            password=settings.RMQ_PASSWORD,
            exchanges=[
                Exchange2Consume(
                    exchange=settings.RMQ_EXCHANGE, routing_key=settings.RMQ_ROUTING_KEY
                ),
            ],
            queue_name=settings.RMQ_QUEUE,
            callback=create_coffee_callback,
            consumer_tag=settings.PROJECT_NAME,
        )

        application.state.pub = pub
        application.state.sub = sub

        application.add_event_handler("startup", connect_rmq(app=application))
        application.add_event_handler("shutdown", disconnect_rmq(app=application))

        return application

    @staticmethod
    def _init_exception_handlers(app: FastAPI) -> None:
        app.add_exception_handler(
            HTTP_500_INTERNAL_SERVER_ERROR, http_internal_error_handler
        )
        app.add_exception_handler(StarletteHTTPException, http_exception_handler)
        app.add_exception_handler(
            RequestValidationError, request_validation_exception_handler
        )


app_factory = ApplicationFactory()
