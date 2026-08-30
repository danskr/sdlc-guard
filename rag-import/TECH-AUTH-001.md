# TECH-AUTH-001 - Authenticated checkout requirement

Artifact type: technical_spec
Project: ecommerce-demo
Feature: FEATURE-CHECKOUT
Status: approved

## Content

The checkout API requires the X-User-Id header for all payment methods. Requests without a user identity return HTTP 401.

## Relationships

- refines: US-CHECKOUT-001
- conflicts_with: US-CHECKOUT-001, BUS-CHECKOUT-001, AC-CHECKOUT-001
