from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import datetime

class LedgerEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    customer_id: int
    invoice_id: int | None
    type: str
    amount: Decimal
    currency: str
    reference_id: str
    created_at: datetime
