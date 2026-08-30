# SDLC-Guard
Maya is the Project Manager, Jack the Business Analyst, and Alex the Solution Architect on a large custom software program. The project started with a reasonably clear scope, but months later the reality looks very different. Requirements keep evolving, new acceptance criteria appear, technical decisions change, implementation gets ahead of documentation, tests lag behind, and technical debt slowly accumulates. Every week, the three of them spend more time trying to answer deceptively simple questions:
- What exactly is approved?
- What changed?
- What is still unclear?
- Which requirement has no implementation?
- Which implementation has no requirement?
- Are the tests still aligned with the current scope?
- And which parts of the solution are actually ready for release?

Alex is becoming increasingly convinced that the SDLC itself needs a dedicated traceability and reasoning layer. A system that continuously connects business requirements, acceptance criteria, technical specifications, source code, tests, NFRs, and implementation evidence—and allows the team to interrogate the evolving project through natural language.

<p align="center">
  <img src="docs/images/cover.png" alt="Cover image" width="55%">
</p>

SDLC-Guard combines deterministic traceability analysis with semantic retrieval and LLM reasoning. SDLC artifacts and connected source/test files are ingested into PostgreSQL and RAGFlow, while LangGraph orchestrates analysis of questions such as “Is checkout ready for release?”, “Which approved capabilities have no implementation?”, or “Is there source code that has no approved requirement?” It combines:

1. RAGFlow semantic retrieval for evidence discovery.
2. A PostgreSQL traceability store for deterministic completeness checks.
3. LangGraph orchestration for analysis workflows.
4. An OpenAI model for grounded reasoning and explanation.

The included demo project is a small e-commerce implementation with web frontend, backend business logic, wallet integration, and payment integration. The corpus is deliberately imperfect so the system has known scope gaps, implementation gaps, test gaps, orphan code, and contradictory requirements to discover.

## What SDLC-Guard can answer

Examples:
- Do you see inconsistencies in the current project scope?
- Are there gaps in the current project scope?
- What pieces are missing from checkout?
- Which approved functionality has no automated test?
- Which approved functionality has no source-code implementation?
- Is there code that does not map to approved scope?
- Which non-functional requirements lack verification?
- What would be affected if wallet payments were removed?
- Is checkout ready for release?

## Architecture

SDLC-Guard architecture is build with the following core design principle:

> **Deterministic software establishes structural SDLC facts, semantic retrieval finds supporting context, and the LLM explains the implications.**


<p align="center">
  <img src="docs/images/architecture.png" alt="Architecture image" width="45%">
</p>

### User / curl / UI

This is the entry point into SDLC-Guard. Users can interact with the system through the browser-based React UI, direct `curl` requests, or any other client capable of calling the REST API. Questions are expressed in natural language, such as *“Is checkout ready for release?”* or *“Which approved requirements have no implementation?”* The client does not need to know artifact IDs, database structure, or how evidence is stored. Every request is sent to the SDLC-Guard API as a project-analysis question. This layer intentionally keeps the interaction simple while hiding the internal orchestration, traceability, retrieval, and reasoning mechanisms.

### SDLC-Guard: FastAPI + LangGraph

SDLC-Guard is the central orchestration and analysis service. FastAPI exposes the HTTP endpoints used by the UI and command-line clients, while LangGraph coordinates the internal analysis workflow. The service first classifies the user's intent and determines whether the question concerns test coverage, implementation completeness, consistency, orphan code, NFR validation, release readiness, or general semantic analysis. It then invokes the appropriate deterministic analyzers against the traceability model. In parallel, or as required, it retrieves semantically relevant artifacts from RAGFlow. LangGraph coordinates these steps and assembles the evidence that will be presented to the reasoning model. This component therefore acts as the control plane connecting deterministic SDLC analysis, semantic retrieval, and LLM reasoning.

### RAGFlow: Semantic Retrieval

RAGFlow provides the semantic retrieval layer. It indexes SDLC artifacts and connected source or test content as embedded documents, allowing evidence to be found based on meaning rather than exact identifiers or keywords. For example, a question about payment timeout recovery can retrieve the corresponding technical specification, acceptance criteria, implementation, and tests even if the user does not mention their artifact IDs. Retrieval results include relevant chunks and similarity scores. These chunks are treated as evidence rather than authoritative structural facts. RAGFlow therefore complements the explicit PostgreSQL traceability graph by surfacing context that may not be discoverable through direct relationships alone. Its primary role is to broaden the evidence available to SDLC-Guard when answering natural-language questions.

### PostgreSQL: Storage for project artifacts

PostgreSQL stores artifacts such as requirements, user stories, acceptance criteria, technical specifications, source-code components, tests, NFRs, and observations together with their explicit relationships. This allows SDLC-Guard to answer structural questions without relying on probabilistic LLM interpretation. For example, it can determine whether an approved requirement has no linked implementation, whether code exists without an approved upstream requirement, or whether an NFR has no verification artifact. The traceability model is also used to identify contradictions and release-readiness blockers. PostgreSQL therefore serves as the authoritative source for explicit SDLC relationships and completeness checks. This deterministic layer is one of the key differences between SDLC-Guard and a conventional RAG-only system.

### OpenAI: LLM for Reasoning

OpenAI provides the reasoning and explanation layer. The model receives the original question together with deterministic findings from PostgreSQL and semantic evidence retrieved from RAGFlow. Its role is not to invent the project structure or decide whether a relationship exists. Instead, it interprets the supplied evidence, connects related findings, explains their impact, and produces a natural-language response. It can also suggest remediation steps and identify practical delivery risks implied by the evidence. Because the model reasons over evidence collected by the previous stages, its answers remain grounded in the actual project artifacts. This creates a clear separation between deterministic facts and probabilistic reasoning.

### Grounded Findings

Grounded findings are the final analysis result returned to the user. A response may include an overall conclusion, categorized findings, severity levels, affected artifacts, recommendations, and supporting evidence. Findings can originate from deterministic analyzers, semantic evidence, or a combination of both. For example, PostgreSQL may establish that `TECH-PAYMENT-001` has no linked implementation, while RAGFlow retrieves the specification and source-code context explaining what functionality is actually missing. The LLM then turns those facts into an understandable explanation of the delivery risk. The result can therefore be inspected rather than treated as an opaque AI answer. In the browser UI, the output is separated into **Analysis**, **Findings**, and **Evidence** views so users can trace conclusions back to their sources.

### Artifacts + Sample Source + Tests

This is the raw project corpus consumed by the ingestion pipeline. In the showcase project it includes business specifications, user stories, acceptance criteria, technical specifications, API definitions, architecture artifacts, NFRs, source-code metadata, test specifications, observations, and actual connected source/test files. Each artifact has structured metadata describing its type, status, relationships, and supporting information. Source and test artifacts can also reference real files from the sample ecommerce application. This allows SDLC-Guard to reason over both formal project documentation and actual implementation evidence. The demo corpus intentionally contains inconsistencies, missing implementations, missing tests, orphan code, and unverified NFRs so that the analysis capabilities can be demonstrated.

### Ingestion → RAGFlow

The RAGFlow branch transforms the SDLC corpus into documents suitable for semantic retrieval. Each artifact is converted into a representation containing its metadata and textual content. For source and test artifacts, the ingestion process also includes the corresponding source-file content so retrieval can reason about the actual implementation rather than metadata alone. The documents are uploaded into the `sdlc-guard-ecommerce-demo` RAGFlow dataset and processed using the configured embedding model. Once parsing and embedding complete, the documents become searchable through RAGFlow's retrieval API. This semantic index is what allows SDLC-Guard to find relevant evidence for broad natural-language questions.

### Ingestion → PostgreSQL

The PostgreSQL branch converts the structured SDLC artifact definitions into the deterministic traceability model. Artifact identifiers, artifact types, statuses, properties, and explicit relationships are stored so that the system can query the project graph directly. This model supports repeatable checks such as missing implementation coverage, missing test coverage, orphan implementations, NFR validation, and release-readiness analysis. Because these checks operate on explicit relationships, the same input always produces the same structural result. The database is rebuilt or refreshed during ingestion so it remains aligned with the latest artifact corpus. PostgreSQL therefore provides the factual backbone against which semantic evidence and LLM reasoning are evaluated.


### Overall Flow

The architecture deliberately combines **three different kinds of capability**:

> PostgreSQL answers: What is explicitly connected, missing, inconsistent, or unverified?
> RAGFlow answers: What project evidence is semantically relevant to this question?
> OpenAI answers: What do these facts and pieces of evidence mean for the project?
> LangGraph orchestrates the flow between deterministic analysis, semantic retrieval, and LLM reasoning.

## Repository layout

- `services/sdlc-guard/` - FastAPI/LangGraph agent service.
- `services/sdlc-guard-ui/` - React/TypeScript conversational web UI.
- `artifacts/` - SDLC specifications and metadata imported into RAGFlow.
- `sample-project/ecommerce/` - runnable sample application source and tests.
- `k8s/base/` - Kubernetes manifests for SDLC-Guard, traceability DB, and sample app.
- `k8s/ragflow/` - RAGFlow Helm override values and installer notes.
- `scripts/` - build, image import, deployment, ingestion, and smoke-test helpers.
- `docs/` - architecture, known demo findings, and detailed deployment instructions.

## SDLC-Guard Web UI

SDLC-Guard includes a React/TypeScript browser interface for conversational analysis of SDLC artifacts.

The interface provides:

- Natural-language questions about project scope and release readiness
- Structured deterministic findings
- RAGFlow semantic evidence
- Artifact references and similarity scores
- Separate Analysis, Findings, and Evidence views

Example questions include:

- Is checkout ready for release?
- Do you see any inconsistencies in the current scope of the project?
- Are there any approved functionalities not covered by test implementation?
- Are there any functionalities that are not implemented at all and have no source code counterpart?
- Is there source code that has no approved requirement?
- Which non-functional requirements have not been verified?

## Why SDLC-Guard Is More Than RAG

SDLC-Guard combines deterministic SDLC traceability analysis with semantic retrieval and LLM reasoning.

<p align="center">
  <img src="docs/images/prompt-flow.png" alt="Prompt flow image" width="45%">
</p>

### Deterministic traceability analysis

PostgreSQL stores explicit relationships between requirements, acceptance criteria, technical specifications, source code, tests, non-functional requirements, and observations.

This allows SDLC-Guard to deterministically identify structural issues such as:

- Missing source-code implementations
- Missing automated test coverage
- Requirement and specification conflicts
- Orphan source-code implementations
- Unverified non-functional requirements
- Release-readiness blockers

### Semantic evidence retrieval

RAGFlow retrieves relevant artifacts based on the meaning of the question rather than requiring the user to know exact artifact identifiers or keywords.

This allows SDLC-Guard to retrieve specifications, source-code artifacts, acceptance criteria, and tests that provide additional context for deterministic findings.

### Evidence-grounded reasoning

LangGraph orchestrates the deterministic traceability analysis and semantic retrieval workflow.

The LLM receives evidence from both sources and produces a natural-language explanation, supporting evidence, risk assessment, and remediation recommendations.

This hybrid architecture avoids relying on an LLM alone to determine structural SDLC facts.

## Known ground truth in the demo

The sample data intentionally contains these examples:

- Guest checkout is allowed by the business story but forbidden by a technical requirement.
- Wallet payments are specified as reserve-then-capture, while implementation performs immediate debit.
- Payment idempotency is required but not implemented.
- Partial refunds are approved but have no source-code implementation.
- Payment timeout handling is approved but has no automated test.
- A promotion-code implementation exists with no approved requirement.
- Checkout throughput is specified but has no performance test.
- Wallet failure auditing is required but has no automated verification.

See `docs/DEMO_GROUND_TRUTH.md` for the full expected result set.

## Quick start

See `docs/INSTALL_K8S.md` for the complete Ubuntu/Kubernetes procedure.

## Launch the Web UI

After SDLC-Guard and the UI are deployed to Kubernetes, start a local port-forward:

    kubectl -n sdlc-guard port-forward svc/sdlc-guard-ui 3000:80

Then open:

    http://localhost:3000

The UI sends questions to the existing SDLC-Guard `/api/v1/query` endpoint and presents the response as conversational analysis with structured Findings and Evidence views.

## Demo Project and Seeded Defects

The ecommerce application included in this repository is intentionally imperfect.

It contains deliberately seeded SDLC problems used to demonstrate SDLC-Guard's analysis capabilities, including:

- Conflicting business and technical requirements
- Missing source-code implementations
- Missing automated test coverage
- Incorrect wallet implementation semantics
- Missing payment idempotency
- Missing timeout reconciliation
- Missing partial refund functionality
- Unverified non-functional requirements
- Source code with no approved upstream requirement

These defects are intentional demonstration inputs and should not be interpreted as recommended implementation patterns.
