import uuid
from sqlalchemy import Column, String, Integer, DateTime, func, ForeignKey, DECIMAL, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..core.database import Base

class GroupBuyParticipant(Base):
    __tablename__ = "group_buy_participants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_buy_id = Column(UUID(as_uuid=True), ForeignKey("group_buys.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False)

    quantity_ordered = Column(Integer, nullable=False)
    total_price = Column(DECIMAL(10, 2), nullable=False)
    
    # paid, refunded
    payment_status = Column(String(20), nullable=False, default='paid')
    tripay_reference_code = Column(String(50), nullable=True)

    # pending, collected
    pickup_status = Column(String(20), nullable=False, default='pending')
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    group_buy = relationship("GroupBuy", back_populates="participants")
    user = relationship("Profile")

    @property
    def full_name(self) -> str:
        return self.user.full_name

    __table_args__ = (UniqueConstraint('group_buy_id', 'user_id', name='_group_buy_user_uc'),) 