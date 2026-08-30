# NFR-AUDIT-001 - Wallet failure audit trail

Artifact type: nfr
Project: ecommerce-demo
Feature: FEATURE-WALLET
Status: approved

## Content

Every wallet reserve, capture, release, and failure must emit an audit event containing correlation ID, user ID, order/cart ID, operation, outcome, and timestamp.

## Relationships
