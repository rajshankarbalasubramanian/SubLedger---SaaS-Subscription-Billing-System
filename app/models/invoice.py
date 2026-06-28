# app/models/invoice.py
from sqlalchemy import Column, Integer, ForeignKey, Numeric, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db import Base

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="RESTRICT"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False)
    amount_due = Column(Numeric(10,2), nullable=False)
    amount_paid = Column(Numeric(10,2), nullable=False, default=0.00)
    currency = Column(String(3), nullable=False)
    status = Column(String, nullable=False, default="draft")  # draft, issued, partially_paid, paid, overdue, void
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    subscription = relationship("Subscription", back_populates="invoices")
    customer = relationship("Customer", back_populates="invoices")
    payment_attempts = relationship("PaymentAttempt", back_populates="invoice")
    ledger_entries = relationship("LedgerEntry", back_populates="invoice")
