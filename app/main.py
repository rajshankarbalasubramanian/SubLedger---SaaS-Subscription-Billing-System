from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.exceptions import DomainException
from app.routes import (
    plans_router, 
    customers_router, 
    subscriptions_router, 
    invoices_router, 
    payments_router, 
    ledger_router
)

app = FastAPI(
    title="SubLedger Core API",
    description="Low-Level Designed Subscription & Append-Only Billing Engine",
    version="1.0.0"
)

# Exception mapping mechanism intercepting custom business faults
@app.exception_handler(DomainException)
def handle_domain_business_faults(request: Request, exc: DomainException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "error_type": exc.__class__.__name__}
    )

# Routing bindings
app.include_router(plans_router)
app.include_router(customers_router)
app.include_router(subscriptions_router)
app.include_router(invoices_router)
app.include_router(payments_router)
app.include_router(ledger_router)

@app.get("/health", tags=["Infrastructure"])
def health_check():
    return {"status": "healthy", "service": "subledger-billing-engine"}
