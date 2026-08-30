from fastapi import FastAPI, Header, HTTPException
from .models import CheckoutRequest, PromoRequest
from .payment import authorize_card
from .wallet import debit_wallet
from .promotions import apply_promo

app = FastAPI(title="SDLC-Guard Demo Commerce API", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/v1/checkout")
def checkout(req: CheckoutRequest, x_user_id: str | None = Header(default=None)):
    # INTENTIONAL SCOPE CONTRADICTION:
    # business story allows guest checkout, technical requirement requires identity.
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authenticated user required")

    # INTENTIONAL IMPLEMENTATION GAP:
    # idempotency_key is accepted but never persisted/checked.
    if req.payment_method == "wallet":
        payment = debit_wallet(x_user_id, req.amount)
    else:
        payment = authorize_card(req.amount)

    return {"cart_id": req.cart_id, "payment": payment, "idempotency_key": req.idempotency_key}


@app.post("/api/v1/promotions/apply")
def promotion(req: PromoRequest):
    return apply_promo(req.code, req.subtotal)

# INTENTIONAL MISSING ENDPOINT:
# Approved scope requires POST /api/v1/refunds/partial but it is not implemented.
