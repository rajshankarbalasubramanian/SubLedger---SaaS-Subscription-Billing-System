from datetime import datetime, timezone, timedelta
from app.repositories.invoice_repo import InvoiceRepository
from app.repositories.subscription_repo import SubscriptionRepository
from app.repositories.plan_repo import PlanRepository
from app.services.ledger_service import LedgerService
from app.models.invoice import Invoice
from app.exceptions import BadRequestException, NotFoundException

class InvoiceService:
    def __init__(self, invoice_repo: InvoiceRepository, subscription_repo: SubscriptionRepository, plan_repo: PlanRepository, ledger_service: LedgerService):
        self.invoice_repo = invoice_repo
        self.subscription_repo = subscription_repo
        self.plan_repo = plan_repo
        self.ledger_service = ledger_service

    def generate_invoice(self, subscription_id: int, period_start: datetime | None = None, period_end: datetime | None = None) -> Invoice:
        subscription = self.subscription_repo.get(subscription_id)
        if not subscription or subscription.status != "active":
            raise BadRequestException("Subscription is not found or is currently inactive.")

        plan = self.plan_repo.get(subscription.plan_id)
        if not plan or not plan.is_active:
            raise BadRequestException("Cannot generate an invoice for an inactive plan context.")

        # Default calculations if no bounds provided
        now = datetime.now(timezone.utc)
        p_start = period_start or subscription.current_period_start
        p_end = period_end or subscription.current_period_end
        due_date = now + timedelta(days=14)

        # Rule: Invoice amount_due comes directly from the plan price snapshot at time of generation
        invoice_obj = Invoice(
            subscription_id=subscription.id,
            customer_id=subscription.customer_id,
            amount_due=plan.price,
            amount_paid=0.00,
            currency=plan.currency,
            status="issued",
            period_start=p_start,
            period_end=p_end,
            due_date=due_date
        )
        
        # Atomically commit records inside database layer
        created_invoice = self.invoice_repo.create(invoice_obj)

        # Audit lifecycle inside tracking ledger
        self.ledger_service.record_entry(
            customer_id=subscription.customer_id,
            invoice_id=created_invoice.id,
            entry_type="invoice_created",
            amount=created_invoice.amount_due,
            currency=created_invoice.currency,
            reference_id=f"inv_init_{created_invoice.id}"
        )

        return created_invoice
