# app/schemas/borongan.py

import uuid
from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

# --- Skema untuk membuat Borongan ---
class BoronganCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    price_per_unit: Decimal = Field(..., gt=0, decimal_places=2)
    unit: str = Field(..., max_length=20)
    target_quantity: int = Field(..., gt=1)
    deadline: datetime
    pickup_point_address: str

# --- Skema untuk request body saat join ---
class BoronganJoin(BaseModel):
    quantity_ordered: int = Field(..., gt=0, description="Jumlah unit yang ingin dibeli")

# --- Skema untuk respons setelah join ---
class BoronganJoinResponse(BaseModel):
    message: str
    payment_url: str  # Kita akan gunakan URL placeholder untuk sekarang
    group_buy_status: str  # Memberi tahu frontend status terbaru dari borongan

# --- Skema untuk menampilkan detail Partisipan ---
class ParticipantSchema(BaseModel):
    user_id: uuid.UUID
    full_name: str
    quantity_ordered: int
    
    class Config:
        from_attributes = True

# --- Skema untuk menampilkan Detail Borongan ---
class BoronganDetailSchema(BaseModel):
    id: uuid.UUID
    supplier_id: uuid.UUID
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    price_per_unit: Decimal
    unit: str
    target_quantity: int
    current_quantity: int
    participants_count: int
    participants: List[ParticipantSchema] = []  # Daftar partisipan
    deadline: datetime
    pickup_point_address: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- Skema untuk menampilkan borongan dalam daftar ---
class BoronganSummarySchema(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str] = None
    price_per_unit: Decimal
    unit: str
    target_quantity: int
    current_quantity: int
    participants_count: int
    deadline: datetime
    pickup_point_address: str
    status: str
    created_at: datetime
    image_url: Optional[str] = None

    class Config:
        from_attributes = True

# Skema untuk respons daftar borongan
class BoronganListResponse(BaseModel):
    borongan: List[BoronganSummarySchema] 