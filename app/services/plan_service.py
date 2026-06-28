from decimal import Decimal
from app.repositories.plan_repo import PlanRepository
from app.models.plan import Plan
from app.exceptions import BadRequestException, NotFoundException

class PlanService:
    def __init__(self, plan_repo: PlanRepository):
        self.plan_repo = plan_repo

    def create_plan(self, name: str, price: Decimal, currency: str = "USD") -> Plan:
        # Rule: Plan price must be greater than 0
        if price <= 0:
            raise BadRequestException("Plan price must be strictly greater than 0.")
        
        plan = Plan(name=name, price=price, currency=currency, is_active=True)
        return self.plan_repo.create(plan)

    def get_plan(self, plan_id: int) -> Plan:
        plan = self.plan_repo.get(plan_id)
        if not plan:
            raise NotFoundException(f"Plan with ID {plan_id} not found.")
        return plan
