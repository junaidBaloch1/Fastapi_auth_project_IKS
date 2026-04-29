from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite for simplicity — swap for PostgreSQL in production
# DATABASE_URL = "sqlite:///./auth.db"
# DATABASE_URL = "mysql+pymysql://root:@127.0.0.1:3306/fastapi_db"
# DATABASE_URL = "mysql+pymysql://root@127.0.0.1:3306/fastapi_db".strip()

DB_USER = "root"
DB_PASSWORD = ""   # empty in your case
DB_HOST = "127.0.0.1"
DB_PORT = "3306"
DB_NAME = "fastapi_db"

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as connection:
        print("OK: Database connection successful")
except Exception as e:
    print("Connection failed:", str(e))

# SessionLocal is a factory — each request gets its own session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All models inherit from this Base
Base = declarative_base()


def get_db():
    """
    Dependency function — FastAPI calls this automatically.
    Yields a DB session per request, closes it when done.
    'yield' makes this a context manager — cleanup runs after response.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()