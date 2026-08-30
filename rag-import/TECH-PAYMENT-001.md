# TECH-PAYMENT-001 - Payment idempotency persistence

Artifact type: technical_spec
Project: ecommerce-demo
Feature: FEATURE-PAYMENT
Status: approved

## Content

Checkout must persist idempotency_key before calling the external payment gateway. A repeated key returns the original result and never re-authorizes.

## Relationships

- refines: AC-PAYMENT-003
