from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects import postgresql
from sqlmodel import Field, Relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User  # noqa: F401


class Coffee(Base, table=True):
    id: int = Field(sa_column=Column(Integer, primary_key=True))
    uid: UUID | None = Field(
        sa_column=Column(postgresql.UUID(as_uuid=True), nullable=True)
    )
    blend_name: str = Field(sa_column=Column(String(200)))
    origin: str | None = Field(sa_column=Column(String(200), nullable=True))
    variety: str | None = Field(sa_column=Column(String(50), nullable=True))
    notes: list[str] | None = Field(
        sa_column=Column(postgresql.ARRAY(String), nullable=True)
    )
    intensifier: str | None = Field(sa_column=Column(String(100), nullable=True))
    users: list["User"] = Relationship(back_populates="coffee")
