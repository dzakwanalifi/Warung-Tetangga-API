# app/models/listing.py

import uuid
from sqlalchemy import Column, String, Integer, DateTime, func, Text, ForeignKey, DECIMAL, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geography
from sqlalchemy.orm import relationship

from ..core.database import Base

class Listing(Base):
    __tablename__ = "listings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    unit = Column(String(20), nullable=False) # e.g., 'kg', 'ikat', 'buah'
    stock_quantity = Column(Integer, nullable=False, default=1)
    
    # Kita akan gunakan array teks untuk URL gambar dari Azure Blob Storage nanti
    image_urls = Column(ARRAY(Text), nullable=True)
    
    status = Column(String(20), nullable=False, default='available') # 'available', 'sold_out'
    location = Column(Geography(geometry_type='POINT', srid=4326), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # Membuat relasi agar kita bisa mengakses profil penjual dari objek listing
    seller = relationship("Profile") 