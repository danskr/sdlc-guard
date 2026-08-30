# AC-PAYMENT-003 - Idempotent checkout payment

Artifact type: acceptance_criterion
Project: ecommerce-demo
Feature: FEATURE-PAYMENT
Status: approved

## Content

Two checkout submissions with the same idempotency key must result in at most one payment authorization and one order.

## Relationships

- derived_from: US-PAYMENT-001
