# SDLC-Guard Validation Report

This report summarizes the final validation of the SDLC-Guard portfolio demo.

## Validation results

- Product/display naming consistency: PASS
- Runtime identifier consistency: PASS
- Python package consistency: PASS
- Kubernetes naming consistency: PASS
- RAGFlow dataset integration: PASS
- Python syntax compilation: PASS
- Artifact YAML parsing: PASS
- Artifact graph validation: PASS
- Traceability PostgreSQL ingestion: PASS
- RAGFlow document ingestion and embedding: PASS
- RAGFlow semantic retrieval: PASS
- Deterministic traceability analysis: PASS
- Evidence-grounded LLM analysis: PASS
- SDLC-Guard regression/unit tests: PASS
- Sample e-commerce backend tests: PASS
- Shell-script syntax validation: PASS
- Kubernetes Kustomize rendering: PASS
- Kubernetes client-side manifest validation: PASS
- Container image builds: PASS
- Kubernetes deployments and rollouts: PASS
- SDLC-Guard Web UI production build: PASS
- SDLC-Guard Web UI Kubernetes deployment: PASS

## Artifact corpus

The demo corpus contains:

- 37 SDLC artifacts
- 45 explicit traceability relationships

The corpus intentionally contains requirement conflicts, implementation gaps, test gaps, orphan implementation, and unverified NFRs.

See `docs/DEMO_GROUND_TRUTH.md` for the intentionally seeded showcase defects.

## Deterministic analysis results

Expected structural findings validated during evaluation:

- Test coverage: 8 findings
- Implementation coverage: 10 findings
- Orphan implementation: 1 finding
- Consistency: 6 explicit conflicts
- NFR coverage: 2 findings
- Release readiness: checkout correctly classified as not release-ready

## Semantic retrieval validation

RAGFlow semantic retrieval was validated using natural-language project questions.

The deployed SDLC-Guard service successfully combined:

1. deterministic traceability evidence from PostgreSQL
2. semantic evidence retrieved from RAGFlow
3. LLM reasoning over the combined evidence

Validated examples included payment gateway timeout behavior, checkout release readiness, missing implementations, missing tests, scope inconsistencies, NFR verification, and orphan source code.

All final evaluation queries returned with RAGFlow evidence enabled.

## Regression tests

The SDLC-Guard test suite includes regression coverage for:

- natural-language orphan implementation classification
- distinction between orphan code and missing implementation
- RAGFlow public retrieval endpoint usage
- RAGFlow dataset request structure
- RAGFlow application-level API error handling

The final SDLC-Guard test suite passes successfully.

## Web UI validation

The React/TypeScript SDLC-Guard Web UI:

- builds successfully using Vite
- runs from an Nginx container
- proxies `/api/` requests to the SDLC-Guard backend
- deploys successfully in the `sdlc-guard` Kubernetes namespace
- provides conversational project analysis
- exposes Analysis, Findings, and Evidence views
- displays deterministic findings and RAGFlow evidence

## Kubernetes deployment

Validated workloads include:

- `traceability-postgres`
- `sdlc-guard`
- `sdlc-guard-ui`
- `ecommerce-backend`
- `ecommerce-frontend`
- SDLC corpus ingestion Job

RAGFlow and its supporting services were also successfully deployed and used for live semantic retrieval.

## Final status

SDLC-Guard is validated as an end-to-end portfolio demo combining deterministic SDLC traceability analysis, semantic RAG retrieval, agent orchestration, evidence-grounded LLM reasoning, and an interactive browser UI.
