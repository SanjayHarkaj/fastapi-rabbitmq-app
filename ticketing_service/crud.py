from typing import Optional
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt

from ticketing_service.database import SessionLocal
from ticketing_service.models import User, TicketLink
from ticketing_service.schemas import UserCreate, UserBase, TicketLinkData, TicketRequest
from config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY

# Initialize password context for hashing and verification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Initialize OAuth2 password bearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


# User Auth Queries #
def get_user(db: Session, username: str) -> Optional[User]:
    """Fetches a user from the database by username."""
    return db.query(User).filter(User.username == username).first()


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticates a user with username and password."""
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies the password."""
    return pwd_context.verify(plain_password, hashed_password)


def create_bearer_token(data: dict) -> str:
    """Creates a jwt bearer token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_user(db: Session, user: UserCreate) -> User:
    """Creates a new user in database."""
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_current_user(token: str = Depends(oauth2_scheme)) -> UserBase:
    """Fetches the current user from the token."""
    token_data = verify_token(token)
    if token_data is None:
        guest_user = {"username": "guest", "role": "guest"}
        return UserBase(**guest_user)
    return token_data


def verify_token(token: str) -> Optional[UserBase]:
    """Fetches the current user from the token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        role: str = payload.get("role")
        if username is None:
            return None
        token_data = UserBase(username=username, role=role)
    except Exception:
        return None
    return token_data


# User Auth Queries #


# Ticket Link Queries #

def create_ticket_link(ticket_request: TicketRequest) -> None:
    """Creates a ticket link in database."""
    db_ticket_link = TicketLink(username=ticket_request.username, requested_time=ticket_request.requested_time)
    db = SessionLocal()
    db.add(db_ticket_link)
    db.commit()
    db.refresh(db_ticket_link)


def activate_ticket_link(ticket_link: TicketLinkData) -> None:
    """Activate ticket link, by adding access token and availability in database."""
    db = SessionLocal()
    try:
        db_ticket_link = fetch_ticket_link(db, ticket_link.username)
        db_ticket_link.access_token = ticket_link.access_token
        db_ticket_link.available_from = ticket_link.available_from
        db.commit()
        db.refresh(db_ticket_link)
    except NoResultFound:
        raise Exception(f"Ticket link with user {ticket_link.username} not found.")


def fetch_ticket_link(db: Session, username: str, access_token: str | None = None) -> Optional[TicketLink]:
    """Fetches a ticket link from the database."""
    if access_token:
        return db.query(TicketLink).filter(TicketLink.username == username,
                                           TicketLink.access_token == access_token).first()
    return db.query(TicketLink).filter(TicketLink.username == username).first()
# Ticket Link Queries #
