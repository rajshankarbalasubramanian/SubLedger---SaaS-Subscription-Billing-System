from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.repositories.customer_repo import CustomerRepository
from app.services.customer_service import CustomerService
from app.schemas.customer import CustomerCreate, CustomerResponse

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.post("", response_model=CustomerResponse, status_code=201)
def register_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    return CustomerService(CustomerRepository(db)).register_customer(payload.name, payload.email)

@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    return CustomerService(CustomerRepository(db)).get_customer(customer_id)
