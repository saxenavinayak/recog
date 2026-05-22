# import psycopg2
# import os



# pg_pwd = os.getenv("POSTGRES_PW")
# pg_usr = os.getenv("POSTGRES_USER")
# pg_host = os.getenv("POSTGRES_HOST")
# pg_port = os.getenv("POSTGRES_PORT")


# def postgres_connection():
#     conn = psycopg2.connect(
#             database="postgres",
#             user=pg_usr,
#             password=pg_pwd,
#             host=pg_host,
#             port=pg_port
#         )

#     return conn





import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

POSTGRES_PW = os.getenv("POSTGRES_PW")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PW}@{POSTGRES_HOST}:{POSTGRES_PORT}/postgres"
engine = create_engine(SQLALCHEMY_DATABASE_URL)


# # This creates a local file named 'test.db' in your project folder
# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# # SQLite specific: 'check_same_thread' is needed because FastAPI is async
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
        