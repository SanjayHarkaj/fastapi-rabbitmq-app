import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get the directory of the currently executing script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Navigate to the parent directory of ticketing_service
parent_dir = os.path.dirname(current_dir)

# Navigate to the ticketing_service directory
ticketing_service_dir = os.path.join(parent_dir, 'ticketing_service')

# Create the database path
db_path = "sqlite:///" + os.path.join(ticketing_service_dir, "ticketing.db")

SQLALCHEMY_DATABASE_URL = db_path

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
