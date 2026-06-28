from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.ledger_entry import LedgerEntry
from app.schemas.ledger_entry import LedgerEntryResponse

router = APIRouter(prefix="/ledger", tags=["Ledger"])

@router.get("/customer/{customer_id}", response_model=list[LedgerEntryResponse])
def get_customer_ledger(customer_id: int, db: Session = Depends(get_db)):
    # Direct extraction query for historical financial transparency
    return db.query(LedgerEntry).filter(LedgerEntry.customer_id == customer_id).all()
