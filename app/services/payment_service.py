from decimal import Decimal
from app.repositories.payment_attempt_repo import PaymentAttemptRepository
from app.repositories.invoice_repo import InvoiceRepository
from app.services.ledger_service import LedgerService
from app.models.payment_attempt import PaymentAttempt
from app.exceptions import BadRequestException, NotFoundException

class PaymentService:
    def __init__(self, payment_attempt_repo: PaymentAttemptRepository, invoice_repo: InvoiceRepository, ledger_service: LedgerService):
        self.payment_attempt_repo = payment_attempt_repo
        self.invoice_repo = invoice_repo
        self.ledger_service = ledger_service

    def record_payment(self, invoice_id: int, amount: Decimal, status: str, provider_reference: str) -> PaymentAttempt:
        # Idempotency safety check
        existing_attempt = self.payment_attempt_repo.get_by_provider_reference(provider_reference)
        if existing_attempt:
            raise BadRequestException(f"Payment with reference '{provider_reference}' has already been processed.")

        invoice = self.invoice_repo.get(invoice_id)
        if not invoice:
            raise NotFoundException(f"Invoice with ID {invoice_id} not found.")

        # Rule: Prevent payment operations against terminated/void items
        if invoice.status in ["paid", "void"]:
            raise BadRequestException(f"Cannot apply adjustments to a clear '{invoice.status}' invoice state.")

        # Rule: A successful payment cannot exceed the remaining unpaid amount on the invoice
        remaining_balance = invoice.amount_due - invoice.amount_paid
        if status == "success" and amount > remaining_balance:
            raise BadRequestException(f"Payment amount {amount} exceeds remaining unpaid balance of {remaining_balance}.")

        # Persist payment attempt history mapping
        attempt = PaymentAttempt(
            invoice_id=invoice.id,
            amount=amount,
            currency=invoice.currency,
            status=status,
            provider_reference=provider_reference,
            failure_reason="Transaction declined by banking provider." if status == "failed" else None
        )
        created_attempt = self.payment_attempt_repo.create(attempt)

        # Rule: Distinguish happy paths vs unhappy failure logic states explicitly
        if status == "failed":
            self.ledger_service.record_entry(
                customer_id=invoice.customer_id,
                invoice_id=invoice.id,
                entry_type="payment_failure",
                amount=amount,
                currency=invoice.currency,
                reference_id=f"pay_fail_{provider_reference}"
            )
            return created_attempt

        # Happy path processing: update balance metrics safely
        new_total_paid = invoice.amount_paid + amount
        
        # Rule: Fully paid shifts state to paid; partial remains partially_paid
        new_status = "paid" if new_total_paid == invoice.amount_due else "partially_paid"
        
        self.invoice_repo.update_invoice_payment(invoice, new_total_paid, new_status)

        # Append transactional visibility log trace entry
        self.ledger_service.record_entry(
            customer_id=invoice.customer_id,
            invoice_id=invoice.id,
            entry_type="payment_success",
            amount=amount,
            currency=invoice.currency,
            reference_id=f"pay_success_{provider_reference}"
        )

        return created_attempt
