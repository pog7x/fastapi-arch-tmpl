from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship

from app.models.base import Base

if TYPE_CHECKING:
    from .coffee import Coffee  # noqa: F401


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(postgresql.UUID(as_uuid=True), nullable=True)
    password = Column(String(50), nullable=True)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    username = Column(String(50), nullable=True)
    email = Column(String, nullable=True)
    gender = Column(String(50), nullable=True)
    phone_number = Column(String(50), nullable=True)
    social_insurance_number = Column(String(50), nullable=True)
    date_of_birth = Column(String(50), nullable=True)
    employment = Column(postgresql.JSONB, nullable=True)
    address = Column(postgresql.JSONB, nullable=True)
    coffee_id = Column(Integer, ForeignKey("coffee.id"))
    coffee = relationship("Coffee", back_populates="users")
