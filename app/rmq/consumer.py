import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional

import aio_pika
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class Exchange2Consume(BaseModel):
    exchange: str
    routing_key: Optional[str]


class RMQConsumer:
    MAX_CONNECT_RETRIES = 20

    def __init__(
        self,
        login: str,
        password: str,
        virtualhost: str,
        host: str,
        port: int,
        queue_name: str,
        callback: Callable[..., Any],
        exchanges: List[Exchange2Consume],
        consumer_tag: Optional[str] = None,
        queue_args: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._login: str = login
        self._password: str = password
        self._virtualhost: str = virtualhost
        self._host: str = host
        self._port: int = port
        self._consumer_tag: Optional[str] = consumer_tag

        self._queue_name: str = queue_name
        self._callback: Callable[..., Any] = callback
        self._queue_args: Optional[Dict[str, Any]] = queue_args
        self._exhanges: List[Exchange2Consume] = exchanges

        self._channel: Optional[aio_pika.RobustChannel] = None
        self._connection: Optional[aio_pika.RobustConnection] = None

    async def start(self) -> "RMQConsumer":
        await self._connect()

        await self._channel.set_qos(prefetch_count=1)

        queue: aio_pika.RobustQueue = await self._channel.declare_queue(
            name=self._queue_name,
            durable=True,
            arguments=self._queue_args,
        )

        if self._exhanges:
            for exc in self._exhanges:
                await queue.bind(exchange=exc.exchange, routing_key=exc.routing_key)

        await queue.consume(callback=self._callback, consumer_tag=self._consumer_tag)

        return self

    async def stop(self) -> "RMQConsumer":
        await self._disconnect()
        return self

    async def _connect(self) -> None:
        for retry in range(self.MAX_CONNECT_RETRIES):
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
                logger.info("RMQConsumer: Connected to RMQ")
                return
            except Exception as err:
                logger.info(
                    f"RMQConsumer: Connect to RMQ error, retry [{retry}], {err}"
                )
                await self._disconnect()
                await asyncio.sleep(1)

        raise Exception("RMQConsumer: Could not connect to RMQ, exceed retries count")

    async def _disconnect(self) -> None:
        if self._channel is not None:
            await self._channel.close()
        if self._connection is not None:
            await self._connection.close()
        self._channel, self._connection = None, None
