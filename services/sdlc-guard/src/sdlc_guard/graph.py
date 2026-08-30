from __future__ import annotations

import json
from langgraph.graph import END, START, StateGraph
from langchain_openai import ChatOpenAI

from .config import get_settings
from .intent import classify
from .models import AgentState
from .prompts import SYSTEM_PROMPT
from .ragflow import RAGFlowClient
from .traceability import analyze


def classify_node(state: AgentState):
    return {"analysis_type": classify(state["question"])}


def traceability_node(state: AgentState):
    findings, evidence = analyze(state["project_id"], state["analysis_type"], state["question"])
    return {"deterministic_findings": findings, "trace_evidence": evidence}


def retrieval_node(state: AgentState):
    client = RAGFlowClient()
    try:
        evidence = client.search(state["question"])
        return {"rag_evidence": evidence, "ragflow_used": bool(evidence)}
    except Exception as exc:
        if get_settings().ragflow_required:
            raise
        return {
            "rag_evidence": [{
                "artifact_id": "RAGFLOW-WARNING",
                "artifact_type": "system",
                "title": "RAGFlow unavailable",
                "excerpt": str(exc),
                "source": "system",
            }],
            "ragflow_used": False,
        }


def reason_node(state: AgentState):
    findings = state.get("deterministic_findings", [])
    evidence = (state.get("trace_evidence", []) + state.get("rag_evidence", []))[:30]
    settings = get_settings()
    if not settings.openai_api_key:
        if findings:
            lines = [f"I found {len(findings)} structural issue(s) using the SDLC traceability model."]
            for f in findings[:12]:
                ids = ", ".join(f.get("artifacts", []))
                lines.append(f"- {f['title']} [{ids}]: {f['description']}")
            lines.append("Configure OPENAI_API_KEY to add semantic reasoning over the retrieved RAGFlow evidence.")
            return {"answer": "\n".join(lines)}
        return {"answer": "No deterministic structural issue was found. Configure OPENAI_API_KEY for semantic analysis of RAGFlow evidence."}

    model = ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key)
    user = {
        "question": state["question"],
        "analysis_type": state["analysis_type"],
        "deterministic_findings": findings,
        "evidence": evidence,
    }
    response = model.invoke([
        ("system", SYSTEM_PROMPT),
        ("user", "Analyze this SDLC question using only the supplied evidence:\n" + json.dumps(user, indent=2)),
    ])
    return {"answer": response.content}


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("classify", classify_node)
    graph.add_node("traceability", traceability_node)
    graph.add_node("retrieve", retrieval_node)
    graph.add_node("reason", reason_node)
    graph.add_edge(START, "classify")
    graph.add_edge("classify", "traceability")
    graph.add_edge("traceability", "retrieve")
    graph.add_edge("retrieve", "reason")
    graph.add_edge("reason", END)
    return graph.compile()


agent_graph = build_graph()
