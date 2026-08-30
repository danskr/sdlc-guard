# SRC-PROMO-001 - Promotion code implementation

Artifact type: source_code
Project: ecommerce-demo
Feature: FEATURE-PROMOTION
Status: approved

## Content

apply_promo implements SAVE10 discount behavior even though no approved user story, business spec, acceptance criterion, or technical specification defines promotions.

## Relationships


Source path: `sample-project/ecommerce/backend/app/promotions.py`

## Connected source/test implementation

```
def apply_promo(code: str, subtotal: float) -> dict:
    # INTENTIONAL ORPHAN IMPLEMENTATION: no approved SDLC requirement maps to this feature.
    if code.upper() == "SAVE10":
        return {"discount": round(subtotal * 0.10, 2), "code": "SAVE10"}
    return {"discount": 0.0, "code": code.upper()}

```
