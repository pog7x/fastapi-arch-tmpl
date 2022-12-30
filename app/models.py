import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Client(Base):
    __tablename__ = "client"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(50), nullable=False)
    surname = sa.Column(sa.String(50), nullable=False)
    credit_card = sa.Column(sa.String(50), nullable=True)
    car_number = sa.Column(sa.String(15), nullable=True)


class Parking(Base):
    __tablename__ = "parking"

    id = sa.Column(sa.Integer, primary_key=True)
    address = sa.Column(sa.String(100), nullable=False)
    opened = sa.Column(sa.Boolean, nullable=True)
    count_places = sa.Column(sa.Integer, nullable=False)
    count_available_places = sa.Column(sa.Integer, nullable=False)


class ClientParking(Base):
    __tablename__ = "client_parking"

    id = sa.Column(sa.Integer, primary_key=True)
    time_in = sa.Column(sa.DateTime, nullable=False)
    time_out = sa.Column(sa.DateTime, nullable=True)
    client_id = sa.Column(sa.Integer, sa.ForeignKey("client.id"), nullable=False)
    parking_id = sa.Column(sa.Integer, sa.ForeignKey("parking.id"), nullable=False)

    client = relationship("Client", backref="client")
    parking = relationship("Parking", backref="parking")
