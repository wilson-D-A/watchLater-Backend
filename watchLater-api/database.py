import os
from urllib.parse import quote_plus
from google.cloud.sql.connector import Connector, IPTypes
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from models import Base

load_dotenv()

CONNECTION_NAME = os.getenv(
    "CLOUD_SQL_CONNECTION_NAME", "project-6d40a2d5-26a5-4210-a34:us-east1:watchlater"
)
HOST = os.getenv("HOST", "34.24.170.131")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_IP_TYPE = os.getenv("DB_IP_TYPE", "PUBLIC").upper()
DB_DRIVER = os.getenv("DB_DRIVER", "pg8000")

# Cloud SQL Python Connector does not support every SQLAlchemy/Postgres driver.
SUPPORTED_CONNECTOR_DRIVERS = {"pg8000", "pymysql", "pytds", "asyncpg", "psycopg"}
if not os.getenv("DATABASE_URL") and DB_DRIVER not in SUPPORTED_CONNECTOR_DRIVERS:
    DB_DRIVER = "pg8000"

DATABASE_URL = os.getenv("DATABASE_URL") or (
    f"postgresql+{DB_DRIVER}://{DB_USER}:{quote_plus(DB_PASSWORD)}@/{DB_NAME}"
    f"?host=/cloudsql/{CONNECTION_NAME}"
)


connector = Connector(refresh_strategy="LAZY")


def getconn():
    ip_type = IPTypes.PRIVATE if DB_IP_TYPE == "PRIVATE" else IPTypes.PUBLIC
    conn = connector.connect(
        CONNECTION_NAME,
        DB_DRIVER,
        user=DB_USER,
        password=DB_PASSWORD,
        db=DB_NAME,
        ip_type=ip_type,
    )
    return conn


if os.getenv("DATABASE_URL"):
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
else:
    engine = create_engine(
        f"postgresql+{DB_DRIVER}://", creator=getconn, pool_pre_ping=True
    )


def init_db():
    if not DB_PASSWORD:
        raise RuntimeError(
            "DB_PASSWORD is empty or missing. Set DB_USER/DB_PASSWORD/DB_NAME and CLOUD_SQL_CONNECTION_NAME before starting the app."
        )
    Base.metadata.create_all(engine)


def close_connector():
    connector.close()


def get_session():
    with Session(engine) as session:
        yield session
