from pydantic import BaseModel, Field


class CheckoutRequest(BaseModel):
    cart_id: str
    payment_method: str = Field(pattern="^(card|wallet)$")
    amount: float = Field(gt=0)
    idempotency_key: str


class RefundRequest(BaseModel):
    payment_id: str
    amount: float = Field(gt=0)


class PromoRequest(BaseModel):
    code: str
    subtotal: float = Field(gt=0)
