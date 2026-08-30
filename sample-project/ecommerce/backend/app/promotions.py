def apply_promo(code: str, subtotal: float) -> dict:
    # INTENTIONAL ORPHAN IMPLEMENTATION: no approved SDLC requirement maps to this feature.
    if code.upper() == "SAVE10":
        return {"discount": round(subtotal * 0.10, 2), "code": "SAVE10"}
    return {"discount": 0.0, "code": code.upper()}
