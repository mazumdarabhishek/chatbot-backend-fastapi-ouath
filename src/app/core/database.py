from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

engine = create_engine(os.getenv("database_url"),
                       pool_pre_ping= True,
                       pool_recycle= 3600,
                       pool_size= 20,
                       max_overflow= 0)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()