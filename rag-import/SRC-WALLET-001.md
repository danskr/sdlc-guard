# SRC-WALLET-001 - Wallet direct debit adapter

Artifact type: source_code
Project: ecommerce-demo
Feature: FEATURE-WALLET
Status: approved

## Content

debit_wallet immediately debits the wallet. It does not implement reserve, capture, or release semantics required by approved scope.

## Relationships

- implements: US-WALLET-001

Source path: `sample-project/ecommerce/backend/app/wallet.py`

## Connected source/test implementation

```
from uuid import uuid4


def debit_wallet(user_id: str, amount: float) -> dict:
    # INTENTIONAL DEMO DEFECT:
    # Business/technical scope says wallet funds must be RESERVE -> CAPTURE.
    # This implementation immediately debits the balance.
    return {
        "status": "debited",
        "wallet_transaction_id": f"wal-{uuid4().hex[:10]}",
        "user_id": user_id,
        "amount": amount,
    }

```
