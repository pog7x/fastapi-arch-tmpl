from sqlalchemy.ext.asyncio import AsyncSession

from app import domain
from app.core.session import with_session
from app.models import ClientParking, Parking
from app.repository.client_parking_repository import ClientParkingRepository
from app.repository.client_repository import ClientRepository
from app.repository.parking_repository import ParkingRepository


class ClientParkingService:
    @with_session
    async def take_parking(
        self,
        client_parking: domain.TakeClientParkingModel,
        session: AsyncSession = None,
    ) -> ClientParking:
        is_already_exists = await ClientParkingRepository().search_items(
            search_data=domain.ClientParkingModel(
                parking_id=client_parking.parking_id,
                client_id=client_parking.client_id,
                time_out=None,
            ).dict(exclude_unset=True),
            session=session,
        )

        if is_already_exists:
            print(400, "parking for this client already exists")
            return
            # raise HTTPException(
            #     status_code=400, detail="parking for this client already exists"
            # )

        res_c = await ClientRepository().get_by_id(
            item_id=client_parking.client_id,
            session=session,
        )

        if not res_c:
            print(404, "client not found")
            return
            # raise HTTPException(status_code=404, detail="client not found")

        res_parking: Parking = await ParkingRepository().get_by_id(
            item_id=client_parking.parking_id,
            session=session,
        )

        if res_parking.count_available_places < 1 or res_parking.opened is False:
            print(404, "available parking is not found")
            return
            # raise HTTPException(status_code=404, detail="available parking is not found")
        res_parking.count_available_places -= 1

        new_client_parking = ClientParking(**client_parking.dict())
        session.add(new_client_parking)

        return new_client_parking

    @with_session
    async def release_parking(
        self,
        client_parking: domain.ReleaseClientParkingModel,
        session: AsyncSession = None,
    ) -> ClientParking:
        is_already_exists = await ClientParkingRepository().search_items(
            search_data=domain.ClientParkingModel(
                parking_id=client_parking.parking_id,
                client_id=client_parking.client_id,
                time_out=None,
            ).dict(exclude_unset=True),
            session=session,
        )
        if not is_already_exists:
            print(400, "parking for this client does not exist")
            return
            # raise HTTPException(
            #     status_code=400, detail="parking for this client does not exist"
            # )

        res_parking: Parking = await ParkingRepository().get_by_id(
            item_id=client_parking.parking_id,
            session=session,
        )

        if not res_parking:
            print(404, "parking is not found")
            return
            # raise HTTPException(status_code=404, detail="parking is not found")
        res_client_parking = is_already_exists[0]
        res_parking.count_available_places += 1
        res_client_parking.time_out = client_parking.time_out

        await session.commit()
        return res_client_parking
