import asyncio
import json
import uuid
import uvicorn

from datetime import datetime, timedelta
from fastapi import FastAPI

from rabbitmq.main import publish_on_queue, consume_from_queue
from config import REQUEST_LINK_QUEUE, ACCESS_TOKEN_QUEUE

app = FastAPI()

Rules = {
    "premium": "instant",
    "standard": "10 minutes",
    "guest": "start of the next day"
}


def generate_access_token() -> str:
    """Generates a random access token."""
    return str(uuid.uuid4())


def calculate_available_from(role: str) -> datetime:
    """Calculates the availability time based on user role."""
    if role in Rules:
        availability = Rules[role]
        current_time = datetime.now()
        if availability == "instant":
            return current_time
        elif availability == "10 minutes":
            return current_time + timedelta(minutes=10)
        else:
            return datetime(current_time.year, current_time.month, current_time.day) + timedelta(days=1)
    else:
        raise Exception("invalid role")


def create_access_token(username: str, role: str) -> dict:
    """Creates an access token and availability time w.r.t role."""
    access_token = generate_access_token()
    # Example: Returning response containing access token and username
    access_token_data = {
        "access_token": access_token,
        "username": username,
        "available_from": calculate_available_from(role).strftime("%Y-%m-%d %H:%M:%S")
    }
    return access_token_data


async def process_ticket_request(user_info: dict) -> None:
    """Processes the ticket request and publishes the access token."""
    username = user_info['username']
    role = user_info['role']
    access_token_data = create_access_token(username, role)
    await publish_on_queue(ACCESS_TOKEN_QUEUE, json.dumps(access_token_data))


@app.on_event("startup")
async def startup_event():
    """Starts up Events."""

    # Subscribes to Request ticket link Queue to receive user info and call function to access token
    asyncio.create_task(consume_from_queue(REQUEST_LINK_QUEUE, process_ticket_request))


if __name__ == "__main__":
    # Run the FastAPI application using uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001)