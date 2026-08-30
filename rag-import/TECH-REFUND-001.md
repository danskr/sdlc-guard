# TECH-REFUND-001 - Partial refund API

Artifact type: technical_spec
Project: ecommerce-demo
Feature: FEATURE-REFUND
Status: approved

## Content

Backend exposes POST /api/v1/refunds/partial with payment_id and amount. It validates the remaining refundable balance before invoking the payment provider.

## Relationships

- refines: AC-REFUND-001
