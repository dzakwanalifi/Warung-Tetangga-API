# app/schemas/profile.py

import uuid
from pydantic import BaseModel
from typing import Optional

# Skema untuk data yang diterima saat update profile
class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    address_text: Optional[str] = None
    latitude: Optional[float] = None  # Kita akan menerima lat/lon terpisah
    longitude: Optional[float] = None

# Skema untuk menampilkan data profile
class ProfileSchema(BaseModel):
    id: uuid.UUID
    full_name: str
    address_text: Optional[str] = None
    # Kita tidak akan menampilkan lat/lon secara langsung, tapi bisa ditambahkan jika perlu
    reputation_score: int

    class Config:
        from_attributes = True # Dulu 'orm_mode', sekarang 'from_attributes' 

# Skema baru untuk ditampilkan di dalam Lapak
class ProfileInLapakSchema(BaseModel):
    id: uuid.UUID
    full_name: str

    class Config:
        from_attributes = True 