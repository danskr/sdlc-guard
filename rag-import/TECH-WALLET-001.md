# TECH-WALLET-001 - Wallet two-phase debit

Artifact type: technical_spec
Project: ecommerce-demo
Feature: FEATURE-WALLET
Status: approved

## Content

Wallet integration exposes reserve, capture, and release operations. Direct debit during checkout is forbidden because the order transaction may still fail.

## Relationships

- refines: AC-WALLET-001
