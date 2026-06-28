from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import datetime

class PlanCreate(BaseModel):
    name: str = Field(..., max_length=100)
    price: Decimal = Field(..., gt=0)
    currency: str = Field("USD", min_length=3, max_length=3)

class PlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True) # Modern V2 Syntax
    
    id: int
    name: str
    price: Decimal
    currency: str
    is_active: bool
    created_at: datetime
