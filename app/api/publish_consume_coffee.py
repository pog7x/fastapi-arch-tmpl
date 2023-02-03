import json

import aio_pika
from fastapi import APIRouter, Body
from starlette.requests import Request

from app.clients.base import BaseAsyncHttpClient
from app.core.base_response import BaseResponse
from app.core.config import settings
from app.repository.coffee_repository import CoffeeRepository
from app.schemas import CoffeeModel

router = APIRouter()


async def create_coffee_callback(msg: aio_pika.IncomingMessage):
    async with msg.process():
        body = json.loads(msg.body)
        await CoffeeRepository().create_object(CoffeeModel(**body))


@router.get("/", response_model=BaseResponse[CoffeeModel])
async def publish_coffee(request: Request) -> Body:
    cli = BaseAsyncHttpClient(base_url="http://random_coffee:6000")
    coffee_resp = await cli.base_request("/random_coffee/", "GET", "random_coffee")
    to_rmq = CoffeeModel(**coffee_resp.json())
    await request.app.state.pub.send_to_rmq(
        to_rmq, routing_key=settings.RMQ_ROUTING_KEY
    )
    return BaseResponse.from_result(result=to_rmq).dict()
