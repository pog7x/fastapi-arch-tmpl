from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import PositiveInt
from sqlalchemy.future import select

from app import schemas
from app.models import Client, ClientParking, Parking, session

router = APIRouter()


@router.get("/clients", response_model=List[schemas.ClientModel])
async def search_clients(name: Optional[str] = None, surname: Optional[str] = None):
    qs = select(Client)
    if name:
        qs = qs.where(Client.name == name)
    if surname:
        qs = qs.where(Client.surname == surname)
    res = await session.execute(qs.order_by(Client.id))
    return res.scalars().all()


@router.post("/clients")
async def create_client(client: schemas.ClientModel) -> Client:
    new_client = Client(**client.dict())
    session.add(new_client)
    await session.commit()
    return new_client


@router.get("/clients/{client_id}", response_model=schemas.ClientModel)
async def get_client(client_id: PositiveInt):
    res = await session.execute(select(Client).filter_by(id=client_id))
    return res.scalars().first()


@router.post("/parkings")
async def create_parking(parking: schemas.ParkingModel) -> Parking:
    new_parking = Parking(**parking.dict())
    session.add(new_parking)
    await session.commit()
    return new_parking


@router.post("/client_parking")
async def take_parking(client_parking: schemas.TakeClientParkingModel) -> ClientParking:
    is_already_exists = await session.execute(
        select(ClientParking)
        .where(
            ClientParking.parking_id == client_parking.parking_id,
        )
        .where(
            ClientParking.client_id == client_parking.client_id,
        )
        .where(
            ClientParking.time_out.is_(None),
        )
    )
    if is_already_exists.scalars().first():
        raise HTTPException(
            status_code=400, detail="parking for this client already exists"
        )

    res_c = await session.execute(select(Client).filter_by(id=client_parking.client_id))
    if not res_c.scalars().first():
        raise HTTPException(status_code=404, detail="client not found")

    res_p = await session.execute(
        select(Parking)
        .where(
            Parking.id == client_parking.parking_id,
        )
        .where(
            Parking.opened.is_(True),
        )
        .where(
            Parking.count_available_places >= 1,
        )
    )
    res_parking = res_p.scalars().first()
    if not res_parking:
        raise HTTPException(status_code=404, detail="available parking is not found")

    res_parking.count_available_places -= 1

    new_client_parking = ClientParking(**client_parking.dict())
    session.add(new_client_parking)
    await session.commit()
    return new_client_parking


@router.delete("/client_parking")
async def release_parking(
    client_parking: schemas.ReleaseClientParkingModel,
) -> ClientParking:
    res_cp = await session.execute(
        select(ClientParking)
        .where(
            ClientParking.parking_id == client_parking.parking_id,
        )
        .where(
            ClientParking.client_id == client_parking.client_id,
        )
        .where(
            ClientParking.time_out.is_(None),
        )
    )
    res_client_parking = res_cp.scalars().first()
    if not res_client_parking:
        raise HTTPException(
            status_code=400, detail="parking for this client does not exist"
        )

    res_p = await session.execute(
        select(Parking).filter_by(id=client_parking.parking_id)
    )
    res_parking = res_p.scalars().first()
    if not res_parking:
        raise HTTPException(status_code=404, detail="parking is not found")

    res_parking.count_available_places += 1
    res_client_parking.time_out = client_parking.time_out

    await session.commit()
    return res_client_parking
