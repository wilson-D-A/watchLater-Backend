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
LOCAL_DEV = os.getenv("LOCAL_DEV", "").lower() in {"1", "true", "yes"}
DB_HOST = os.getenv("DB_HOST") or "127.0.0.1"
DB_PORT = os.getenv("DB_PORT") or "6543"
DB_USER = os.getenv("DB_USER") or "postgres"
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME") or "postgres"
DB_IP_TYPE = (os.getenv("DB_IP_TYPE") or "PUBLIC").upper()
DB_DRIVER = os.getenv("DB_DRIVER") or "pg8000"

# Cloud SQL Python Connector does not support every SQLAlchemy/Postgres driver.
SUPPORTED_CONNECTOR_DRIVERS = {"pg8000", "pymysql", "pytds", "asyncpg", "psycopg"}
if (
    not os.getenv("DATABASE_URL")
    and not LOCAL_DEV
    and DB_DRIVER not in SUPPORTED_CONNECTOR_DRIVERS
):
    DB_DRIVER = "pg8000"

DATABASE_URL = os.getenv("DATABASE_URL")

if LOCAL_DEV and not DATABASE_URL and not DB_PASSWORD:
    raise RuntimeError(
        "LOCAL_DEV is enabled but DB_PASSWORD is empty. Set DB_PASSWORD (or provide DATABASE_URL) before starting the app."
    )

if not DATABASE_URL and LOCAL_DEV:
    DATABASE_URL = (
        f"postgresql+{DB_DRIVER}://{DB_USER}:{quote_plus(DB_PASSWORD)}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )


if (
    not DATABASE_URL
    and os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    and os.path.exists(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", ""))
):
    connector = Connector(refresh_strategy="LAZY")
else:
    print("Local development mode detected: Bypassing Cloud SQL Connector.")
    connector = None


def getconn():
    if connector is None:
        raise RuntimeError(
            "Cloud SQL Connector is not configured. Set DATABASE_URL for local/proxy access or provide GOOGLE_APPLICATION_CREDENTIALS for connector mode."
        )

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


if DATABASE_URL:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
else:
    engine = create_engine(
        f"postgresql+{DB_DRIVER}://", creator=getconn, pool_pre_ping=True
    )


def init_db():
    if not DB_PASSWORD and not DATABASE_URL:
        raise RuntimeError(
            "DB_PASSWORD is empty or missing. Set DATABASE_URL for local/proxy access or set DB_USER/DB_PASSWORD/DB_NAME and CLOUD_SQL_CONNECTION_NAME for connector mode."
        )
    Base.metadata.create_all(engine)


def close_connector():
    if connector is not None:
        connector.close()


def get_session():
    with Session(engine) as session:
        yield session
