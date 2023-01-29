from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship

from app.models.base import Base

if TYPE_CHECKING:
    from .user import User  # noqa: F401


class Coffee(Base):
    id = Column(Integer, primary_key=True)
    uid = Column(postgresql.UUID(as_uuid=True), nullable=True)
    blend_name = Column(String(200), nullable=True)
    origin = Column(String(200), nullable=True)
    variety = Column(String(50), nullable=True)
    notes = Column(postgresql.ARRAY(String), nullable=True)
    intensifier = Column(String(100), nullable=True)
    users = relationship("User", back_populates="coffee")
