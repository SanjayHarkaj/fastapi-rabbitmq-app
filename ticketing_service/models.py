from sqlalchemy import Column, Integer, String, Enum, DateTime
from ticketing_service.database import Base
from enum import Enum as PyEnum


class UserRole(str, PyEnum):
    premium = "premium"
    standard = "standard"
    guest = "guest"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole))


class TicketLink(Base):
    __tablename__ = "ticket_links"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, index=True)
    requested_time = Column(DateTime)
    access_token = Column(String, index=True, nullable=True)
    available_from = Column(DateTime, nullable=True)


