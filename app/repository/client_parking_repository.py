from sqlalchemy import and_
from sqlalchemy.future import select

from app import domain
from app.models import Client, ClientParking, Parking
from app.repository.base_repository import BaseRepository


class ClientParkingRepository(BaseRepository):
    async def take_parking(
        self, client_parking: domain.TakeClientParkingModel
    ) -> ClientParking:
        async with self._session_maker.begin() as session:
            is_already_exists = await session.execute(
                select(ClientParking).where(
                    and_(
                        ClientParking.parking_id == client_parking.parking_id,
                        ClientParking.client_id == client_parking.client_id,
                        ClientParking.time_out.is_(None),
                    )
                )
            )
            if is_already_exists.scalars().first():
                print(400, "parking for this client already exists")
                return
                # raise HTTPException(
                #     status_code=400, detail="parking for this client already exists"
                # )

            res_c = await session.execute(
                select(Client, Client.id == client_parking.client_id)
            )
            if not res_c.scalars().first():
                print(404, "client not found")
                return
                # raise HTTPException(status_code=404, detail="client not found")

            res_p = await session.execute(
                select(Parking).where(
                    and_(
                        Parking.id == client_parking.parking_id,
                        Parking.opened.is_(True),
                        Parking.count_available_places >= 1,
                    )
                )
            )
            res_parking = res_p.scalars().first()
            if not res_parking:
                print(404, "available parking is not found")
                return
                # raise HTTPException(status_code=404, detail="available parking is not found")

            res_parking.count_available_places -= 1

            new_client_parking = ClientParking(**client_parking.dict())
            session.add(new_client_parking)

            return new_client_parking
