# BUS-WALLET-001 - Wallet settlement behavior

Artifact type: business_spec
Project: ecommerce-demo
Feature: FEATURE-WALLET
Status: approved

## Content

Wallet payment must reserve the requested amount during checkout. The reservation is captured only after the order is committed. Failed orders must release the reservation.

## Relationships

- derived_from: US-WALLET-001
