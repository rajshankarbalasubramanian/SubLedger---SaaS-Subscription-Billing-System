from sqlalchemy.orm import Session
from app.models.payment_attempt import PaymentAttempt

class PaymentAttemptRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payment_attempt_obj: PaymentAttempt) -> PaymentAttempt:
        self.db.add(payment_attempt_obj)
        self.db.commit()
        self.db.refresh(payment_attempt_obj)
        return payment_attempt_obj

    def get_by_provider_reference(self, reference: str) -> PaymentAttempt | None:
        return self.db.query(PaymentAttempt).filter(PaymentAttempt.provider_reference == reference).first()
