# Security Notes

This repository is a showcase/lab project, not a production hardening baseline.

- Never commit OpenAI or RAGFlow API keys. `scripts/create-secrets.sh` injects them as Kubernetes Secrets.
- The included PostgreSQL password is a demo credential and must be replaced for any non-lab deployment.
- Services are ClusterIP-only by default and are accessed with `kubectl port-forward`.
- Do not expose the RAGFlow UI, PostgreSQL, or SDLC-Guard directly to an untrusted network without authentication, TLS, and network-policy controls.
- The sample e-commerce application contains intentional functional/security-design shortcomings for SDLC analysis demonstrations. Do not use it as production commerce code.
- The system sends retrieved SDLC evidence to the configured OpenAI API model. Do not ingest confidential source/specification data until your data-handling requirements are reviewed.
