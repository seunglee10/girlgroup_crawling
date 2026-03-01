# db/session.py : SQLAlchemy 엔진 및 세션 공통 생성 로직

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

_engine = None


def get_engine():
    global _engine
    if _engine is not None:
        return _engine

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set. Check your .env file.")

    _engine = create_engine(db_url, future=True)
    return _engine


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())