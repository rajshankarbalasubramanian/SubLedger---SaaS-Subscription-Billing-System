from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.repositories import SubscriptionRepository, PlanRepository, CustomerRepository
from app.services import SubscriptionService
from app.schemas.subscription import SubscriptionCreate, SubscriptionResponse  # Updated import

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

@router.post("", response_model=SubscriptionResponse, status_code=201)  # Fixed status code
def create_subscription(payload: SubscriptionCreate, db: Session = Depends(get_db)):
    sub_repo = SubscriptionRepository(db)
    plan_repo = PlanRepository(db)
    cust_repo = CustomerRepository(db)
    
    sub_service = SubscriptionService(sub_repo, plan_repo, cust_repo)
    return sub_service.create_subscription(payload.customer_id, payload.plan_id)
