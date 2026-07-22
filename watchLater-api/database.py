from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Base

engine = create_engine(
    "postgresql+psycopg2://wilson@localhost:5432/wilson",
    echo=True,
)

Base.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
