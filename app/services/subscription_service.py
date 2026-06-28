from datetime import datetime, timedelta, timezone
from app.repositories.subscription_repo import SubscriptionRepository
from app.repositories.plan_repo import PlanRepository
from app.repositories.customer_repo import CustomerRepository
from app.models.subscription import Subscription
from app.exceptions import BadRequestException, NotFoundException

class SubscriptionService:
    def __init__(self, subscription_repo: SubscriptionRepository, plan_repo: PlanRepository, customer_repo: CustomerRepository):
        self.subscription_repo = subscription_repo
        self.plan_repo = plan_repo
        self.customer_repo = customer_repo

    def create_subscription(self, customer_id: int, plan_id: int) -> Subscription:
        # Validate existence
        if not self.customer_repo.get(customer_id):
            raise NotFoundException(f"Customer with ID {customer_id} does not exist.")
            
        plan = self.plan_repo.get(plan_id)
        if not plan:
            raise NotFoundException(f"Plan with ID {plan_id} does not exist.")

        # Rule: A subscription cannot be created for an inactive plan
        if not plan.is_active:
            raise BadRequestException("Cannot create a subscription for an inactive plan.")

        # Rule: A customer cannot have two active subscriptions to the same plan
        existing_active = self.subscription_repo.get_active_by_customer_and_plan(customer_id, plan_id)
        if existing_active:
            raise BadRequestException("Customer already has an active subscription to this specific plan.")

        now = datetime.now(timezone.utc)
        subscription = Subscription(
            customer_id=customer_id,
            plan_id=plan_id,
            status="active",
            current_period_start=now,
            current_period_end=now + timedelta(days=30)
        )
        return self.subscription_repo.create(subscription)
