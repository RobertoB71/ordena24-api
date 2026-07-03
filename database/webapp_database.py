import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

WEBAPP_DB_HOST = os.getenv("WEBAPP_DB_HOST")
WEBAPP_DB_PORT = os.getenv("WEBAPP_DB_PORT")
WEBAPP_DB_NAME = os.getenv("WEBAPP_DB_NAME")
WEBAPP_DB_USER = os.getenv("WEBAPP_DB_USER")
WEBAPP_DB_PASSWORD = os.getenv("WEBAPP_DB_PASSWORD")

WEBAPP_DATABASE_URL = (
    f"postgresql://{WEBAPP_DB_USER}:{WEBAPP_DB_PASSWORD}"
    f"@{WEBAPP_DB_HOST}:{WEBAPP_DB_PORT}/{WEBAPP_DB_NAME}"
)

webapp_engine = create_engine(WEBAPP_DATABASE_URL)

WebAppSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=webapp_engine
)

WebAppBase = declarative_base()


def get_webapp_db():
    db = WebAppSessionLocal()
    try:
        yield db
    finally:
        db.close()