from typing import TYPE_CHECKING, Optional
from uuid import UUID

from pydantic import Json
from sqlalchemy import Column, String
from sqlalchemy.dialects import postgresql
from sqlmodel import Field, Relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.coffee import Coffee  # noqa: F401


class User(Base, table=True):
    id: int = Field(primary_key=True, index=True)
    uid: UUID | None = Field(
        sa_column=(Column(postgresql.UUID(as_uuid=True), nullable=True))
    )
    password: str | None = Field(sa_column=(Column(String(50), nullable=True)))
    first_name: str = Field(sa_column=(Column(String(50))))
    last_name: str | None = Field(sa_column=(Column(String(50), nullable=True)))
    username: str | None = Field(sa_column=(Column(String(50), nullable=True)))
    email: str | None = Field(sa_column=(Column(String, nullable=True)))
    gender: str | None = Field(sa_column=(Column(String(50), nullable=True)))
    phone_number: str | None = Field(sa_column=(Column(String(50), nullable=True)))
    social_insurance_number: str | None = Field(
        sa_column=(Column(String(50), nullable=True))
    )
    date_of_birth: str | None = Field(sa_column=(Column(String(50), nullable=True)))
    employment: Json | None = Field(sa_column=(Column(postgresql.JSONB, nullable=True)))
    address: Json | None = Field(sa_column=(Column(postgresql.JSONB, nullable=True)))
    coffee_id: int | None = Field(default=None, foreign_key="coffee.id")
    coffee: Optional["Coffee"] | None = Relationship(back_populates="users")
