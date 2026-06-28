import pytest
from decimal import Decimal
from datetime import datetime, timezone

from app.services import PlanService, CustomerService, SubscriptionService, PaymentService, InvoiceService, LedgerService
from app.repositories import PlanRepository, CustomerRepository, SubscriptionRepository, InvoiceRepository, PaymentAttemptRepository, LedgerRepository
from app.exceptions import BadRequestException

# ============================================================================
# 1. SERVICE LAYER BUSINESS RULE TESTS
# ============================================================================

def test_plan_price_must_be_greater_than_zero(db_session):
    """Rule 1: Plan price must be strictly greater than 0."""
    plan_repo = PlanRepository(db_session)
    plan_service = PlanService(plan_repo)
    
    with pytest.raises(BadRequestException) as exc_info:
        plan_service.create_plan(name="Free Plan Tier", price=Decimal("0.00"), currency="USD")
    assert "Plan price must be strictly greater than 0" in exc_info.value.message


def test_customer_email_uniqueness(db_session):
    """Rule 2: Customer email registration must be unique."""
    customer_repo = CustomerRepository(db_session)
    customer_service = CustomerService(customer_repo)
    
    # First creation passes smoothly
    customer_service.register_customer(name="John Doe", email="john@example.com")
    
    # Duplicate registration must fail cleanly
    with pytest.raises(BadRequestException) as exc_info:
        customer_service.register_customer(name="Duplicate John", email="john@example.com")
    assert "is already registered" in exc_info.value.message


def test_cannot_subscribe_to_inactive_plan(db_session):
    """Rule 3: Subscriptions cannot be attached to inactive plan templates."""
    plan_repo = PlanRepository(db_session)
    customer_repo = CustomerRepository(db_session)
    sub_repo = SubscriptionRepository(db_session)
    
    plan_service = PlanService(plan_repo)
    customer_service = CustomerService(customer_repo)
    sub_service = SubscriptionService(sub_repo, plan_repo, customer_repo)
    
    # Create required parent records
    plan = plan_service.create_plan(name="Old Legacy Plan", price=Decimal("19.99"))
    customer = customer_service.register_customer(name="Alice", email="alice@example.com")
    
    # Deactivate the plan record manually
    plan.is_active = False
    db_session.commit()
    
    with pytest.raises(BadRequestException) as exc_info:
        sub_service.create_subscription(customer_id=customer.id, plan_id=plan.id)
    assert "Cannot create a subscription for an inactive plan" in exc_info.value.message


def test_no_duplicate_active_subscriptions_to_same_plan(db_session):
    """Rule 4: Customers cannot maintain concurrent active subscriptions to a single plan."""
    plan_repo = PlanRepository(db_session)
    customer_repo = CustomerRepository(db_session)
    sub_repo = SubscriptionRepository(db_session)
    
    plan_service = PlanService(plan_repo)
    customer_service = CustomerService(customer_repo)
    sub_service = SubscriptionService(sub_repo, plan_repo, customer_repo)
    
    plan = plan_service.create_plan(name="SaaS Core", price=Decimal("49.00"))
    customer = customer_service.register_customer(name="Bob", email="bob@example.com")
    
    # First active purchase passes
    sub_service.create_subscription(customer_id=customer.id, plan_id=plan.id)
    
    # Second immediate active assignment fails
    with pytest.raises(BadRequestException) as exc_info:
        sub_service.create_subscription(customer_id=customer.id, plan_id=plan.id)
    assert "Customer already has an active subscription" in exc_info.value.message


def test_overpayment_is_rejected_and_status_transitions_correctly(db_session):
    """Rule 5 & 6: Overpayments are blocked; valid flows shift status accurately."""
    plan_repo = PlanRepository(db_session)
    customer_repo = CustomerRepository(db_session)
    sub_repo = SubscriptionRepository(db_session)
    invoice_repo = InvoiceRepository(db_session)
    payment_repo = PaymentAttemptRepository(db_session)
    ledger_repo = LedgerRepository(db_session)
    
    plan = PlanService(plan_repo).create_plan("Pro Tier", Decimal("100.00"))
    customer = CustomerService(customer_repo).register_customer("Test User", "test@test.com")
    sub = SubscriptionService(sub_repo, plan_repo, customer_repo).create_subscription(customer.id, plan.id)
    
    ledger_service = LedgerService(ledger_repo)
    invoice_service = InvoiceService(invoice_repo, sub_repo, plan_repo, ledger_service)
    payment_service = PaymentService(payment_repo, invoice_repo, ledger_service)
    
    # Snapshot generation creates invoice containing amount_due = 100.00
    invoice = invoice_service.generate_invoice(subscription_id=sub.id)
    
    # Test 5A: Overpayment rejection
    with pytest.raises(BadRequestException) as exc_info:
        payment_service.record_payment(invoice_id=invoice.id, amount=Decimal("150.00"), status="success", provider_reference="tx_1")
    assert "exceeds remaining unpaid balance" in exc_info.value.message
    
    # Test 5B: Partial payment transitions invoice to 'partially_paid'
    payment_service.record_payment(invoice_id=invoice.id, amount=Decimal("40.00"), status="success", provider_reference="tx_partial")
    assert invoice.status == "partially_paid"
    assert invoice.amount_paid == Decimal("40.00")
    
    # Test 5C: Completing the payment transitions invoice status to 'paid'
    payment_service.record_payment(invoice_id=invoice.id, amount=Decimal("60.00"), status="success", provider_reference="tx_final")
    assert invoice.status == "paid"
    assert invoice.amount_paid == Decimal("100.00")


def test_failed_payment_unhappy_path(db_session):
    """Rule 7: Failed transactions record trace logs but preserve current balance configurations."""
    plan_repo = PlanRepository(db_session)
    customer_repo = CustomerRepository(db_session)
    sub_repo = SubscriptionRepository(db_session)
    invoice_repo = InvoiceRepository(db_session)
    payment_repo = PaymentAttemptRepository(db_session)
    ledger_repo = LedgerRepository(db_session)
    
    plan = PlanService(plan_repo).create_plan("Basic Tier", Decimal("30.00"))
    customer = CustomerService(customer_repo).register_customer("User Fail", "fail@test.com")
    sub = SubscriptionService(sub_repo, plan_repo, customer_repo).create_subscription(customer.id, plan.id)
    
    ledger_service = LedgerService(ledger_repo)
    invoice = InvoiceService(invoice_repo, sub_repo, plan_repo, ledger_service).generate_invoice(sub.id)
    payment_service = PaymentService(payment_repo, invoice_repo, ledger_service)
    
    # Record a failed transaction attempt
    attempt = payment_service.record_payment(invoice_id=invoice.id, amount=Decimal("30.00"), status="failed", provider_reference="tx_error_99")
    
    # Check balances and verify failure records are accurate
    assert attempt.status == "failed"
    assert attempt.failure_reason is not None
    assert invoice.amount_paid == Decimal("0.00")
    assert invoice.status == "issued"


# ============================================================================
# 2. END-TO-END INTEGRATION & WEB ROUTER API TESTS
# ============================================================================

def test_api_plan_creation_and_retrieval(client):
    """Validates router request routing validation patterns and JSON schemas end-to-end."""
    # API Creation Route
    post_response = client.post("/plans", json={
        "name": "Enterprise Cloud Sync",
        "price": 899.99,
        "currency": "USD"
    })
    assert post_response.status_code == 201
    data = post_response.json()
    assert data["id"] is not None
    assert data["name"] == "Enterprise Cloud Sync"
    
    # API Retrieval Route
    get_response = client.get(f"/plans/{data['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["price"] == "899.99"
