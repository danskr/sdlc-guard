from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_card_checkout_success():
    r = client.post(
        "/api/v1/checkout",
        headers={"x-user-id": "user-1"},
        json={"cart_id": "cart-1", "payment_method": "card", "amount": 25.0, "idempotency_key": "idem-1"},
    )
    assert r.status_code == 200
    assert r.json()["payment"]["status"] == "authorized"


def test_card_decline():
    r = client.post(
        "/api/v1/checkout",
        headers={"x-user-id": "user-1"},
        json={"cart_id": "cart-2", "payment_method": "card", "amount": 600.0, "idempotency_key": "idem-2"},
    )
    assert r.status_code == 200
    assert r.json()["payment"]["status"] == "declined"

# Deliberately absent:
# - idempotency test
# - payment gateway timeout test
# - wallet reserve/capture test
# - partial refund test
# - performance test
# - wallet audit-event verification
