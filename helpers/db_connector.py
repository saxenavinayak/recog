import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

# Global model base class to prevent circular import between models.recog_models and this one
Base = declarative_base()



class Db_helper:
    def __init__(self):
        pg_pw = os.getenv("POSTGRES_PW")
        pg_usr = os.getenv("POSTGRES_USER")
        pg_host = os.getenv("POSTGRES_HOST")
        pg_port = os.getenv("POSTGRES_PORT")
        self.url = f"postgresql+psycopg2://{pg_usr}:{pg_pw}@{pg_host}:{pg_port}/postgres"
        self.engine = create_engine(self.url)
        self.session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine) # spins up db connections


    def init_db(self):
        import models.recog_models
        Base.metadata.create_all(bind=self.engine)


    @contextmanager # this decorator allows to work with get_db as `with get_db as db:`
    def get_db(self):
        db = self.session()
        try:
            yield db # When application code does with get_db as db, yield db hands off db - the code then resumes here 
            db.commit()
        except Exception: # Any exceptions in application code are caught here
            db.rollback()
            raise
        finally:
            db.close()