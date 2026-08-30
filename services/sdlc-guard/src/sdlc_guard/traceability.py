from __future__ import annotations

from collections import defaultdict, deque
from sqlalchemy import select

from .db import Artifact, ArtifactRelationship, SessionLocal

SCOPE_TYPES = {"user_story", "business_spec", "acceptance_criterion", "technical_spec", "nfr"}
CODE_TYPES = {"source_code"}
TEST_TYPES = {"automated_test", "test_spec"}


def _to_evidence(a: Artifact) -> dict:
    return {
        "artifact_id": a.artifact_id,
        "artifact_type": a.artifact_type,
        "title": a.title,
        "excerpt": a.content[:900],
        "source": "traceability",
    }


def _rel_index(session):
    rels = list(session.scalars(select(ArtifactRelationship)).all())
    outgoing: dict[str, list[ArtifactRelationship]] = defaultdict(list)
    incoming: dict[str, list[ArtifactRelationship]] = defaultdict(list)
    for r in rels:
        outgoing[r.source_id].append(r)
        incoming[r.target_id].append(r)
    return rels, outgoing, incoming


def analyze(project_id: str, analysis_type: str, question: str) -> tuple[list[dict], list[dict]]:
    with SessionLocal() as session:
        artifacts = list(session.scalars(select(Artifact).where(Artifact.project_id == project_id)).all())
        by_id = {a.artifact_id: a for a in artifacts}
        rels, outgoing, incoming = _rel_index(session)
        findings: list[dict] = []
        evidence_ids: set[str] = set()

        def add(ftype, severity, title, description, ids, recommendation):
            findings.append({
                "finding_type": ftype,
                "severity": severity,
                "title": title,
                "description": description,
                "artifacts": ids,
                "recommendation": recommendation,
            })
            evidence_ids.update(i for i in ids if i in by_id)

        if analysis_type in {"test_coverage", "gaps", "release_readiness"}:
            for a in artifacts:
                if a.status != "approved" or a.artifact_type not in SCOPE_TYPES:
                    continue
                verified = any(
                    r.relation_type in {"verifies", "tests"}
                    and r.source_id in by_id
                    and by_id[r.source_id].artifact_type in TEST_TYPES
                    for r in incoming.get(a.artifact_id, [])
                )
                if not verified and a.artifact_type in {"acceptance_criterion", "nfr"}:
                    add(
                        "missing_test_coverage", "high" if a.artifact_type == "acceptance_criterion" else "medium",
                        f"No test coverage for {a.artifact_id}",
                        f"Approved {a.artifact_type.replace('_', ' ')} '{a.title}' has no traceable test implementation.",
                        [a.artifact_id],
                        "Add a test specification and automated test linked with a verifies relationship.",
                    )

        if analysis_type in {"implementation_coverage", "gaps", "release_readiness"}:
            for a in artifacts:
                if a.status != "approved" or a.artifact_type not in {"acceptance_criterion", "technical_spec"}:
                    continue
                implemented = any(
                    r.relation_type == "implements"
                    and r.source_id in by_id
                    and by_id[r.source_id].artifact_type in CODE_TYPES
                    for r in incoming.get(a.artifact_id, [])
                )
                if not implemented:
                    add(
                        "missing_implementation", "high",
                        f"No implementation for {a.artifact_id}",
                        f"Approved artifact '{a.title}' has no source-code artifact linked as its implementation.",
                        [a.artifact_id],
                        "Implement the behavior or explicitly descope/defer the artifact.",
                    )

        if analysis_type in {"orphan_implementation", "gaps", "release_readiness"}:
            for a in artifacts:
                if a.artifact_type != "source_code":
                    continue
                maps_to_scope = any(r.relation_type == "implements" and r.target_id in by_id for r in outgoing.get(a.artifact_id, []))
                if not maps_to_scope:
                    add(
                        "orphan_implementation", "medium",
                        f"Unapproved/orphan implementation {a.artifact_id}",
                        f"Source-code artifact '{a.title}' is not traceable to approved scope.",
                        [a.artifact_id],
                        "Link the implementation to approved scope or remove/disable unintended functionality.",
                    )

        if analysis_type in {"consistency", "gaps", "release_readiness"}:
            seen = set()
            for r in rels:
                if r.relation_type != "conflicts_with" or r.source_id not in by_id or r.target_id not in by_id:
                    continue
                key = tuple(sorted((r.source_id, r.target_id)))
                if key in seen:
                    continue
                seen.add(key)
                a, b = by_id[r.source_id], by_id[r.target_id]
                add(
                    "scope_inconsistency", "high",
                    f"Conflict between {a.artifact_id} and {b.artifact_id}",
                    f"'{a.title}' conflicts with '{b.title}'.",
                    [a.artifact_id, b.artifact_id],
                    "Resolve the contradiction and update dependent design, implementation, and tests.",
                )

        if analysis_type == "nfr_coverage":
            for a in artifacts:
                if a.artifact_type != "nfr" or a.status != "approved":
                    continue
                verified = any(r.relation_type in {"verifies", "tests"} for r in incoming.get(a.artifact_id, []))
                if not verified:
                    add(
                        "unverified_nfr", "high", f"Unverified NFR {a.artifact_id}",
                        f"Non-functional requirement '{a.title}' has no linked verification artifact.",
                        [a.artifact_id],
                        "Add measurable automated verification and link the result to this NFR.",
                    )

        if analysis_type == "change_impact":
            tokens = [t.strip(".,?!'").lower() for t in question.split() if len(t) > 3]
            seeds = [a.artifact_id for a in artifacts if any(t in (a.title + " " + a.content).lower() for t in tokens)]
            if seeds:
                visited = set(seeds)
                q = deque((s, 0) for s in seeds)
                impacted = set(seeds)
                while q:
                    current, depth = q.popleft()
                    if depth >= 2:
                        continue
                    neighbors = [r.target_id for r in outgoing.get(current, [])] + [r.source_id for r in incoming.get(current, [])]
                    for n in neighbors:
                        if n in by_id and n not in visited:
                            visited.add(n); impacted.add(n); q.append((n, depth + 1))
                ids = sorted(impacted)[:30]
                add(
                    "change_impact", "info", "Potentially affected SDLC artifacts",
                    f"Traceability traversal found {len(ids)} artifacts within two relationship hops of the matched scope.",
                    ids,
                    "Review these artifacts before approving the proposed change.",
                )

        evidence = [_to_evidence(by_id[i]) for i in sorted(evidence_ids) if i in by_id]
        return findings, evidence
