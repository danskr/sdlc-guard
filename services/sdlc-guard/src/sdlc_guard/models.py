from __future__ import annotations
from typing import Any, Literal, TypedDict
from pydantic import BaseModel, Field

AnalysisType = Literal[
    "gaps",
    "test_coverage",
    "implementation_coverage",
    "orphan_implementation",
    "consistency",
    "nfr_coverage",
    "change_impact",
    "release_readiness",
    "general",
]


class QueryRequest(BaseModel):
    question: str = Field(min_length=3)
    project_id: str = "ecommerce-demo"


class Evidence(BaseModel):
    artifact_id: str
    artifact_type: str
    title: str
    excerpt: str
    source: str = "traceability"
    score: float | None = None


class Finding(BaseModel):
    finding_type: str
    severity: Literal["critical", "high", "medium", "low", "info"] = "medium"
    title: str
    description: str
    artifacts: list[str] = []
    recommendation: str = ""


class QueryResponse(BaseModel):
    question: str
    analysis_type: AnalysisType
    answer: str
    findings: list[Finding]
    evidence: list[Evidence]
    ragflow_used: bool


class AgentState(TypedDict, total=False):
    question: str
    project_id: str
    analysis_type: AnalysisType
    deterministic_findings: list[dict[str, Any]]
    trace_evidence: list[dict[str, Any]]
    rag_evidence: list[dict[str, Any]]
    ragflow_used: bool
    answer: str
