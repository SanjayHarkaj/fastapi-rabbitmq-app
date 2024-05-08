from datetime import datetime
from pydantic import BaseModel
from ticketing_service.models import UserRole


class UserBase(BaseModel):
    username: str
    role: UserRole


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int


class Token(BaseModel):
    bearer_token: str
    token_type: str


class TicketRequest(BaseModel):
    username: str
    requested_time: datetime


class TicketLinkData(BaseModel):
    access_token: str
    username: str
    available_from: datetime



