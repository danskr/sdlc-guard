# AC-PAYMENT-004 - Gateway timeout handling

Artifact type: acceptance_criterion
Project: ecommerce-demo
Feature: FEATURE-PAYMENT
Status: approved

## Content

If the payment gateway times out, the checkout must enter a reconciliation-safe pending state and retries must not create duplicate authorizations.

## Relationships

- derived_from: US-PAYMENT-001
