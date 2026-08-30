# API-CHECKOUT-001 - Checkout API contract

Artifact type: api_contract
Project: ecommerce-demo
Feature: FEATURE-CHECKOUT
Status: approved

## Content

POST /api/v1/checkout accepts cart_id, payment_method, amount, and idempotency_key. The current implementation also requires X-User-Id even though business scope permits guest card checkout.

## Relationships

- refines: TECH-AUTH-001, TECH-PAYMENT-001
