from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.repositories import PaymentAttemptRepository, InvoiceRepository, LedgerRepository
from app.services import PaymentService, LedgerService
from app.schemas.payment_attempt import RecordPaymentRequest, PaymentAttemptResponse  # Updated import

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/record", response_model=PaymentAttemptResponse, status_code=201)  # Fixed status code
def record_payment(payload: RecordPaymentRequest, db: Session = Depends(get_db)):
    payment_repo = PaymentAttemptRepository(db)
    invoice_repo = InvoiceRepository(db)
    ledger_repo = LedgerRepository(db)
    
    ledger_service = LedgerService(ledger_repo)
    payment_service = PaymentService(payment_repo, invoice_repo, ledger_service)
    
    return payment_service.record_payment(
        payload.invoice_id, 
        payload.amount, 
        payload.status, 
        payload.provider_reference
    )
