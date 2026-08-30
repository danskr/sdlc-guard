# API-REFUND-001 - Refund API contract

Artifact type: api_contract
Project: ecommerce-demo
Feature: FEATURE-REFUND
Status: approved

## Content

POST /api/v1/refunds/partial accepts payment_id and amount and returns refund_id, refunded_amount, and remaining_refundable_amount.

## Relationships

- refines: TECH-REFUND-001
