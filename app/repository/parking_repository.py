from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Parking
from pydantic import PositiveInt
from sqlalchemy.future import select
from typing import Optional, List, Dict


class ParkingRepository:
    def __init__(self, session_maker: sessionmaker) -> None:
        self._session_maker = session_maker

    async def create_parking(self, create_data: Dict) -> Parking:
        new_parking = Parking(**create_data)
        async with self._session_maker.begin() as session:
            session.add(new_parking)
            return new_parking
