# Demo Ground Truth

The e-commerce corpus is intentionally incomplete and inconsistent. These defects are seeded so that SDLC-Guard can be evaluated against known expected findings.

## Primary seeded findings

| ID | Finding | Relevant artifacts |
|---|---|---|
| GF-001 | Guest checkout is allowed by business scope but technical scope requires authentication. | US-CHECKOUT-001, BUS-CHECKOUT-001, AC-CHECKOUT-001, TECH-AUTH-001 |
| GF-002 | Payment idempotency is required but is not implemented; the code accepts the key without storing/checking it. | AC-PAYMENT-003, TECH-PAYMENT-001, SRC-BACKEND-CHECKOUT |
| GF-003 | Gateway timeout/reconciliation behavior has no automated test coverage. | AC-PAYMENT-004, TECH-PAYMENT-002 |
| GF-004 | Wallet scope requires reserve/capture/release but code directly debits the wallet. | AC-WALLET-001, TECH-WALLET-001, SRC-WALLET-001 |
| GF-005 | Partial refund capability is approved but no backend endpoint/source implementation exists. | US-REFUND-001, AC-REFUND-001, TECH-REFUND-001, API-REFUND-001 |
| GF-006 | Promotion code behavior is implemented without approved scope. | SRC-PROMO-001 |
| GF-007 | Checkout performance NFR has no linked performance test. | NFR-PERF-001 |
| GF-008 | Wallet audit-event NFR has no verification artifact. | NFR-AUDIT-001 |

The traceability analyzer may also report additional structurally missing links. That is intentional: the corpus is small enough to understand, but not tailored to force exactly eight findings for every broad query.
