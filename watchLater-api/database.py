import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://wilson@localhost:5432/wilson",
)

engine = create_engine(DATABASE_URL)

Base.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
