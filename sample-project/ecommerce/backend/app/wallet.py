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
