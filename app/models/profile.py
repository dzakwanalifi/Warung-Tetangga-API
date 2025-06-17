import uuid
from sqlalchemy import Column, String, Integer, DateTime, func, Text
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geography

from ..core.database import Base

class Profile(Base):
    __tablename__ = "profiles"

    # Kolom id ini akan diisi dengan UUID dari auth.users Supabase
    id = Column(UUID(as_uuid=True), primary_key=True) 
    
    full_name = Column(String(100), nullable=False)
    profile_picture_url = Column(Text, nullable=True)
    address_text = Column(Text, nullable=True)
    location = Column(Geography(geometry_type='POINT', srid=4326), nullable=True, index=True)
    reputation_score = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now()) 