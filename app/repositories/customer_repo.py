from sqlalchemy.orm import Session
from app.models.customer import Customer

class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, customer_obj: Customer) -> Customer:
        self.db.add(customer_obj)
        self.db.commit()
        self.db.refresh(customer_obj)
        return customer_obj

    def get(self, customer_id: int) -> Customer | None:
        return self.db.query(Customer).filter(Customer.id == customer_id).first()

    def get_by_email(self, email: str) -> Customer | None:
        return self.db.query(Customer).filter(Customer.email == email).first()
