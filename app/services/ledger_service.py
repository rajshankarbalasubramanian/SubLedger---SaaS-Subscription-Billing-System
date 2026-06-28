from decimal import Decimal
import uuid
from app.repositories.ledger_repo import LedgerRepository
from app.models.ledger_entry import LedgerEntry
from app.exceptions import BadRequestException

class LedgerService:
    def __init__(self, ledger_repo: LedgerRepository):
        self.ledger_repo = ledger_repo

    def record_entry(self, customer_id: int, invoice_id: int | None, entry_type: str, amount: Decimal, currency: str, reference_id: str) -> LedgerEntry:
        # Rule: Ledger entries are append-only and traceable through unique reference_id (Idempotency defense)
        existing = self.ledger_repo.get_by_reference_id(reference_id)
        if existing:
            raise BadRequestException(f"Ledger entry with reference tracking ID '{reference_id}' already applied.")

        ledger_entry = LedgerEntry(
            customer_id=customer_id,
            invoice_id=invoice_id,
            type=entry_type,
            amount=amount,
            currency=currency,
            reference_id=reference_id
        )
        return self.ledger_repo.create(ledger_entry)
