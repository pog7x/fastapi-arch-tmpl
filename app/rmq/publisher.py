import asyncio
import logging
from typing import Optional

import aio_pika
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class RmqPublisher:
    MAX_CONNECT_RETRIES = 20

    def __init__(
        self,
        host: str,
        port: int,
        virtualhost: str,
        login: str,
        password: str,
        exchange_name: str,
        exchange_type: aio_pika.ExchangeType,
    ) -> None:
        self._host: str = host
        self._port: int = port
        self._virtualhost: str = virtualhost
        self._login: str = login
        self._password: str = password

        self._exchange_name: str = exchange_name
        self._exchange_type: aio_pika.ExchangeType = exchange_type

        self._channel: Optional[aio_pika.Channel] = None
        self._connection: Optional[aio_pika.Connection] = None

        self._exchange: Optional[aio_pika.Exchange] = None

    async def start(self) -> "RmqPublisher":
        await self._connect()

        self._exchange = await self._channel.declare_exchange(
            name=self._exchange_name,
            type=self._exchange_type,
            durable=True,
        )
        return self

    async def stop(self) -> "RmqPublisher":
        await self._disconnect()
        return self

    async def send_to_rmq(self, data: BaseModel, routing_key: str = "") -> None:
        logger.info(
            (
                f"Send message to RMQ routing_key: {routing_key} with payload:"
                f" {data.json().encode()}"
            ),
        )
        try:
            message = aio_pika.Message(data.json().encode())
        except Exception as err:
            logger.info(f"Send message to RMQ error: {err}")
            raise err

        await self._exchange.publish(message=message, routing_key=routing_key)

    async def _connect(self) -> None:
        for _ in range(self.MAX_CONNECT_RETRIES):
            try:
                self._connection = await aio_pika.connect_robust(
                    host=self._host,
                    port=self._port,
                    virtualhost=self._virtualhost,
                    login=self._login,
                    password=self._password,
                    loop=asyncio.get_event_loop(),
                )
                self._channel = await self._connection.channel()
                logger.info(f"Connected to RMQ, exchange: {self._exchange_name}")
                return
            except Exception as err:
                logger.error(err)
                await self._disconnect()
                await asyncio.sleep(1)

        raise Exception(f"Could not connect to RMQ, exchange: {self._exchange_name}")

    async def _disconnect(self) -> None:
        if self._connection is not None:
            await self._channel.close()
            await self._connection.close()
            self._channel = None
            self._connection = None
