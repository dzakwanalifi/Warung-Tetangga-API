# app/core/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Membuat URL koneksi database dari settings
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Membuat engine SQLAlchemy
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Membuat SessionLocal class yang akan menjadi sesi database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class yang akan digunakan oleh model ORM kita
Base = declarative_base()

# Dependency untuk mendapatkan database session di setiap request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 