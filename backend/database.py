
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Project root folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Load local MySQL configuration explicitly
load_dotenv(BASE_DIR / ".env", override=True)

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

if not all([MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_DATABASE]):
    raise RuntimeError(
        "Missing MySQL configuration. Check MYSQL_HOST, MYSQL_PORT, "
        "MYSQL_USER, and MYSQL_DATABASE in the .env file."
    )

DATABASE_URL = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@"
    f"{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


if __name__ == "__main__":
    try:
        with engine.connect() as connection:
            print("MySQL connected successfully!")
            print(
                "Connected database:",
                connection.exec_driver_sql("SELECT DATABASE()").scalar(),
            )
            columns = connection.exec_driver_sql(
                "SHOW COLUMNS FROM users"
            ).fetchall()
            print("Users table columns:", [row[0] for row in columns])
    except Exception as exc:
        print("MySQL connection failed!")
        print("Error:", exc)