### SubLedger Billing Backend Engine

SubLedger is an append-only transaction logging billing backend engineered using the clean **Controller-Service-Repository** 
pattern. It handles plans, active customer lifecycle routing, subscription allocations, invoice snapshotting, and 
transaction tracking.

###  Local Quickstart Guide

### 1\. Active Virtual Environment Initialization

Ensure your Windows PowerShell window allows script execution before firing up your environment wrapper:

powershell

    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
    .venv\Scripts\Activate.ps1
    

Use code with caution.

### 2\. Run Automated Integration Testing Suite

Execute the testing routines using your targeted environment binary:

powershell

    .venv\Scripts\python.exe -m pytest -v
    

Use code with caution.

### 3\. Start Application Server Local Development

Boot the live engine application context using Uvicorn:

powershell

    uvicorn app.main:app --reload
    

Use code with caution.

Once initialized, visit the interactive Swagger documentation layout directly inside your browser window at: `http://127.0.0`.

* * *

###  Docker Container Orchestration Setup

To bring up both your multi-tier core web application engine along with a sandboxed, persistent PostgreSQL instance, run:

powershell

    docker-compose up --build
    

Use code with caution.

* * *

###  Production Core Application Feature Summary

*   **Price Snapshot Safeguard**: Invoices record prices at creation, shielding active subscription balances from future base-tier package price updates.
*   **Idempotent Webhook Processing**: `PaymentService` checks tracking tokens to avoid applying adjustments from duplicate messaging hooks.
*   **Granular Business Rule Isolations**: Database layers focus solely on CRUD operations, while domain logic states remain isolated inside the service layer.
