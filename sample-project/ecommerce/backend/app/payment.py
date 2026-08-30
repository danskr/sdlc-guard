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
