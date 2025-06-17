from pydantic import BaseModel
from typing import Optional

class PaymentStatusResponse(BaseModel):
    participant_id: str
    payment_status: str
    tripay_status: Optional[str] = None
    tripay_reference: Optional[str] = None 