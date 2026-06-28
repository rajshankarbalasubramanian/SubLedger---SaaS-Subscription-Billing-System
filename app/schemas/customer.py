from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime

class CustomerCreate(BaseModel):
    name: str = Field(..., max_length=100)
    email: EmailStr

class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    email: str
    created_at: datetime
