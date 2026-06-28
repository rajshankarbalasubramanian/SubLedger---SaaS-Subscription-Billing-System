from pydantic import BaseModel, ConfigDict
from datetime import datetime

class SubscriptionCreate(BaseModel):
    customer_id: int
    plan_id: int

class SubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    customer_id: int
    plan_id: int
    status: str
    current_period_start: datetime
    current_period_end: datetime
    created_at: datetime
