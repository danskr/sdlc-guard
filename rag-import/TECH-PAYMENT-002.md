# TECH-PAYMENT-002 - Timeout reconciliation

Artifact type: technical_spec
Project: ecommerce-demo
Feature: FEATURE-PAYMENT
Status: approved

## Content

Gateway timeouts are persisted as pending_reconciliation and resolved asynchronously using provider transaction lookup before the client is allowed to retry.

## Relationships

- refines: AC-PAYMENT-004
