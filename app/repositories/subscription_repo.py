from sqlalchemy.orm import Session
from app.models.subscription import Subscription

class SubscriptionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, subscription_obj: Subscription) -> Subscription:
        self.db.add(subscription_obj)
        self.db.commit()
        self.db.refresh(subscription_obj)
        return subscription_obj

    def get(self, subscription_id: int) -> Subscription | None:
        return self.db.query(Subscription).filter(Subscription.id == subscription_id).first()

    def get_active_by_customer_and_plan(self, customer_id: int, plan_id: int) -> Subscription | None:
        return self.db.query(Subscription).filter(
            Subscription.customer_id == customer_id,
            Subscription.plan_id == plan_id,
            Subscription.status == "active"
        ).first()

    def update_status(self, subscription: Subscription, status: str) -> Subscription:
        subscription.status = status
        self.db.commit()
        self.db.refresh(subscription)
        return subscription
