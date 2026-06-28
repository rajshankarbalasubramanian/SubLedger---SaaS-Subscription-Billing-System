from app.repositories.customer_repo import CustomerRepository
from app.models.customer import Customer
from app.exceptions import BadRequestException, NotFoundException

class CustomerService:
    def __init__(self, customer_repo: CustomerRepository):
        self.customer_repo = customer_repo

    def register_customer(self, name: str, email: str) -> Customer:
        # Rule: Customer email must be unique
        existing = self.customer_repo.get_by_email(email)
        if existing:
            raise BadRequestException(f"Customer email '{email}' is already registered.")
        
        customer = Customer(name=name, email=email)
        return self.customer_repo.create(customer)

    def get_customer(self, customer_id: int) -> Customer:
        customer = self.customer_repo.get(customer_id)
        if not customer:
            raise NotFoundException(f"Customer with ID {customer_id} not found.")
        return customer
