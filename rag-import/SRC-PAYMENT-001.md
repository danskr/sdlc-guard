# SRC-PAYMENT-001 - Card payment adapter

Artifact type: source_code
Project: ecommerce-demo
Feature: FEATURE-PAYMENT
Status: approved

## Content

authorize_card returns declined for demo amounts >= 500 and authorized with payment_id otherwise.

## Relationships

- implements: AC-PAYMENT-001, AC-PAYMENT-002

Source path: `sample-project/ecommerce/backend/app/payment.py`

## Connected source/test implementation

```
from uuid import uuid4


def authorize_card(amount: float) -> dict:
    # Demo implementation: values >= 500 are declined.
    if amount >= 500:
        return {"status": "declined", "reason": "issuer_declined"}
    return {"status": "authorized", "payment_id": f"pay-{uuid4().hex[:10]}", "amount": amount}


def handle_gateway_timeout(amount: float) -> dict:
    # Intentionally simplistic. The approved requirement expects retry-safe
    # timeout handling with reconciliation; no automated test covers it.
    return {"status": "pending_reconciliation", "amount": amount}

```
