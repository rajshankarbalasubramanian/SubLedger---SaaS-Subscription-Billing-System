from sqlalchemy.orm import Session
from app.models.plan import Plan

class PlanRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, plan_obj: Plan) -> Plan:
        self.db.add(plan_obj)
        self.db.commit()
        self.db.refresh(plan_obj)
        return plan_obj

    def get(self, plan_id: int) -> Plan | None:
        return self.db.query(Plan).filter(Plan.id == plan_id).first()

    def get_all_active(self) -> list[Plan]:
        return self.db.query(Plan).filter(Plan.is_active == True).all()
