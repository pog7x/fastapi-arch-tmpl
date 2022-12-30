from fastapi import APIRouter, HTTPException
from sqlalchemy.future import select

from app import domain
from app.core.session import async_session, session
from app.models import ClientParking, Parking
from app.repository.client_parking_repository import ClientParkingRepository

router = APIRouter()

client_parking_repo = ClientParkingRepository(session_maker=async_session)


@router.post("/client_parking")
async def take_parking(client_parking: domain.TakeClientParkingModel) -> ClientParking:
    return await client_parking_repo.take_parking(client_parking=client_parking)


@router.delete("/client_parking")
async def release_parking(
    client_parking: domain.ReleaseClientParkingModel,
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
