from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.repositories import InvoiceRepository, SubscriptionRepository, PlanRepository, LedgerRepository
from app.services import InvoiceService, LedgerService
from app.schemas.invoice import GenerateInvoiceRequest, InvoiceResponse  # Updated import

router = APIRouter(prefix="/invoices", tags=["Invoices"])

@router.post("/generate", response_model=InvoiceResponse, status_code=201)  # Fixed status code
def generate_invoice(payload: GenerateInvoiceRequest, db: Session = Depends(get_db)):
    invoice_repo = InvoiceRepository(db)
    sub_repo = SubscriptionRepository(db)
    plan_repo = PlanRepository(db)
    ledger_repo = LedgerRepository(db)
    
    ledger_service = LedgerService(ledger_repo)
    invoice_service = InvoiceService(invoice_repo, sub_repo, plan_repo, ledger_service)
    
    return invoice_service.generate_invoice(payload.subscription_id, payload.period_start, payload.period_end)
