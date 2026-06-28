from sqlalchemy.orm import Session
from app.models.ledger_entry import LedgerEntry

class LedgerRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, ledger_obj: LedgerEntry) -> LedgerEntry:
        # Append-only: No update or delete methods allowed here
        self.db.add(ledger_obj)
        self.db.commit()
        self.db.refresh(ledger_obj)
        return ledger_obj

    def get_by_reference_id(self, reference_id: str) -> LedgerEntry | None:
        return self.db.query(LedgerEntry).filter(LedgerEntry.reference_id == reference_id).first()
