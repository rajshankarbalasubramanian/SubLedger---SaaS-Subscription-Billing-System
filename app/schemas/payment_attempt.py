from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import datetime

class RecordPaymentRequest(BaseModel):
    invoice_id: int
    amount: Decimal = Field(..., gt=0)
    status: str
    provider_reference: str

class PaymentAttemptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    invoice_id: int
    amount: Decimal
    currency: str
    status: str
    provider_reference: str
    failure_reason: str | None
    created_at: datetime
