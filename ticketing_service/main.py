import asyncio
import datetime
import uvicorn

from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import parse_obj_as
from sqlalchemy.orm import Session

from rabbitmq.main import publish_on_queue, consume_from_queue
from config import REQUEST_LINK_QUEUE, ACCESS_TOKEN_QUEUE
from ticketing_service.schemas import User, UserCreate, Token, UserBase, TicketLinkData, TicketRequest
from ticketing_service.crud import get_current_user, get_user, create_user, authenticate_user, create_bearer_token, \
    create_ticket_link, fetch_ticket_link, activate_ticket_link
from ticketing_service.database import Base, engine, get_db

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/register", response_model=User)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Registers a new user."""
    db_user = get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return create_user(db=db, user=user)


@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Logs in a user and returns a bearer token."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    bearer_token = create_bearer_token(data={"username": user.username, 'role': user.role})
    return {"bearer_token": bearer_token, "token_type": "bearer"}


@app.get("/request_for_ticketing_link")
async def request_ticketing_link(current_user: UserBase = Depends(get_current_user), db: Session = Depends(get_db)):
    """Push user info to message broker queue to be varified by Rule service"""
    ticket_link = fetch_ticket_link(db, current_user.username)
    if ticket_link:
        return {"message": "ticket already requested"}
    await publish_on_queue(REQUEST_LINK_QUEUE, current_user.json())
    ticket_request = TicketRequest(username=current_user.username, requested_time=datetime.datetime.now())
    create_ticket_link(ticket_request)
    return {"message": "link requested"}


@app.get("/get_ticketing_link")
async def get_ticketing_link(request: Request, current_user: UserBase = Depends(get_current_user), db: Session = Depends(get_db)):
    """Gets the ticketing link from database"""
    ticket_link = fetch_ticket_link(db, current_user.username)
    if ticket_link:
        if ticket_link.access_token:
            current_host = request.headers["host"]
            return {"link": f"{current_host}/buy_ticket/{ticket_link.access_token}"}
        else:
            return {"message": "Your request is under processing"}
    else:
        return {"message": "link not available, please request a link"}


@app.get("/buy_ticket/{access_token}")
def buy_ticket(access_token: str, current_user: UserBase = Depends(get_current_user), db: Session = Depends(get_db)):
    """Buys a ticket."""
    ticket_link = fetch_ticket_link(db, current_user.username, access_token)
    if ticket_link:
        current_time = datetime.datetime.now()
        if ticket_link.available_from >= current_time:
            difference_in_seconds = (ticket_link.available_from - current_time).total_seconds()
            difference_in_min = difference_in_seconds // 60
            if difference_in_min >= 60:
                return {"message": f"Page will be available from {ticket_link.available_from}"}
            if difference_in_min < 1:
                return {"message": f"Page will be active in {int(difference_in_seconds)} seconds"}
            else:
                difference_in_seconds = difference_in_seconds % 60
                return {"message": f"Page will be active in {int(difference_in_min)} minutes and {int(difference_in_seconds)} seconds"}
        return {"message": f"Hello, {current_user.username}. Welcome to the ticket page"}
    else:
        return {"message": "invalid access token"}


async def add_ticket_link_info(ticket_link_data: dict) -> None:
    """Creates a ticket link."""
    ticket_link_data = parse_obj_as(TicketLinkData, ticket_link_data)
    activate_ticket_link(ticket_link_data)


@app.on_event("startup")
async def startup_event():
    """Starts up Events."""

    # Subscribes to Access Token Queue to receive access token and call function to create ticket link
    asyncio.create_task(consume_from_queue(ACCESS_TOKEN_QUEUE, add_ticket_link_info))


if __name__ == "__main__":
    # Run the FastAPI application using uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
