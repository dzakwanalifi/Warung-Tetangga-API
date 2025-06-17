import uuid
from sqlalchemy import Column, String, Integer, DateTime, func, Text, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..core.database import Base

class GroupBuy(Base):
    __tablename__ = "group_buys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Untuk MVP, kita asumsikan supplier adalah user biasa. Nanti bisa ditambahkan role.
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    price_per_unit = Column(DECIMAL(10, 2), nullable=False)
    unit = Column(String(20), nullable=False)
    
    target_quantity = Column(Integer, nullable=False)
    current_quantity = Column(Integer, nullable=False, default=0)
    
    deadline = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), nullable=False, default='active')  # active, successful, failed, completed
    pickup_point_address = Column(Text, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    supplier = relationship("Profile")
    participants = relationship("GroupBuyParticipant", back_populates="group_buy") 