# SDLC-Guard Architecture

## Purpose

SDLC-Guard reconstructs traceability across the software delivery lifecycle and uses that structure plus semantic retrieval to answer engineering questions that ordinary document Q&A cannot answer reliably.

## Core components

### SDLC-Guard analysis service

The runtime agent/service is also named **SDLC-Guard**. It is a Python/FastAPI service orchestrated by LangGraph. A request flows through four nodes:

1. **Classify** - maps the question to an analysis mode.
2. **Traceability analysis** - executes deterministic relationship/completeness checks in PostgreSQL.
3. **RAG retrieval** - retrieves semantically relevant evidence from RAGFlow.
4. **Reasoning** - asks the OpenAI model to explain the combined evidence without inventing artifacts.

### RAGFlow

RAGFlow stores searchable representations of the SDLC artifacts. Each imported Markdown document includes:

- artifact ID and type,
- project/feature/status metadata,
- specification content,
- explicit relationships,
- source path,
- the actual connected source-code/test file contents when a source path exists.

### Traceability PostgreSQL

The traceability store contains two main tables:

- `artifacts`
- `artifact_relationships`

Relationships include `derived_from`, `refines`, `implements`, `verifies`, and `conflicts_with`.

This is deliberately separate from RAGFlow. Semantic search is not a completeness mechanism. For example, discovering an acceptance criterion with *no* test is a negative/exhaustive query and must not depend on vector-search recall.

## Analysis modes

- `gaps`
- `test_coverage`
- `implementation_coverage`
- `orphan_implementation`
- `consistency`
- `nfr_coverage`
- `change_impact`
- `release_readiness`
- `general`

## Extending the project

The next natural extensions are:

- Git repository ingestion with commit/SHA metadata.
- Jira/Azure DevOps story ingestion.
- CI test-result ingestion.
- Git diff based change-impact analysis.
- Requirement/version temporal consistency.
- Automated release gates.
- Neo4j or PostgreSQL recursive graph queries for richer dependency analysis.
- Multiple specialized agents under the SDLC-Guard platform.
