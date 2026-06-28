from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.repositories.plan_repo import PlanRepository
from app.services.plan_service import PlanService
from app.schemas.plan import PlanCreate, PlanResponse

router = APIRouter(prefix="/plans", tags=["Plans"])

@router.post("", response_model=PlanResponse, status_code=201)
def create_plan(payload: PlanCreate, db: Session = Depends(get_db)):
    return PlanService(PlanRepository(db)).create_plan(payload.name, payload.price, payload.currency)

@router.get("/{plan_id}", response_model=PlanResponse)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    return PlanService(PlanRepository(db)).get_plan(plan_id)
