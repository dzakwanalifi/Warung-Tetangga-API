# app/schemas/lapak.py

import uuid
from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal
from .profile import ProfileInLapakSchema  # Impor skema baru

# Skema untuk data yang diterima saat membuat lapak baru
class LapakCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0, decimal_places=2)
    unit: str = Field(..., max_length=20)
    stock_quantity: int = Field(..., gt=0)

# Skema untuk data yang diterima saat mengupdate lapak
class LapakUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    unit: Optional[str] = Field(None, max_length=20)
    stock_quantity: Optional[int] = Field(None, gt=0)
    status: Optional[str] = Field(None, pattern="^(available|sold_out|inactive)$")

# Skema dasar untuk menampilkan informasi lapak
class LapakSchema(BaseModel):
    id: uuid.UUID
    seller_id: uuid.UUID
    title: str
    description: Optional[str] = None
    price: Decimal
    unit: str
    stock_quantity: int
    image_urls: Optional[List[str]] = None
    status: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: str
    updated_at: str
    seller: ProfileInLapakSchema

    class Config:
        from_attributes = True

# Skema untuk respons endpoint /lapak/nearby
class LapakListResponse(BaseModel):
    lapak: List[LapakSchema]
    total: int
    page: int = 1
    limit: int = 12 