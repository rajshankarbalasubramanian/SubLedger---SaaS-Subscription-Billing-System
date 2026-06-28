from sqlalchemy.orm import Session
from app.models.invoice import Invoice
from decimal import Decimal

class InvoiceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, invoice_obj: Invoice) -> Invoice:
        """Saves a newly generated invoice structure to the database layer."""
        self.db.add(invoice_obj)
        self.db.commit()
        self.db.refresh(invoice_obj)
        return invoice_obj

    def get(self, invoice_id: int) -> Invoice | None:
        """Retrieves an invoice record based on its primary key constraint identifier."""
        return self.db.query(Invoice).filter(Invoice.id == invoice_id).first()

    def update_invoice_payment(self, invoice: Invoice, new_amount_paid: Decimal, status: str) -> Invoice:
        """Updates internal balances and status parameters during a payment event."""
        invoice.amount_paid = new_amount_paid
        invoice.status = status
        self.db.commit()
        self.db.refresh(invoice)
        return invoice
