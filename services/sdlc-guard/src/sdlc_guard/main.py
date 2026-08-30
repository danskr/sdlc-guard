from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException

from . import __version__
from .db import init_db
from .graph import agent_graph
from .models import Evidence, Finding, QueryRequest, QueryResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="SDLC-Guard", version=__version__, lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok", "service": "SDLC-Guard", "version": __version__}


@app.post("/api/v1/query", response_model=QueryResponse)
def query(req: QueryRequest):
    try:
        result = agent_graph.invoke({"question": req.question, "project_id": req.project_id})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    evidence = []
    seen = set()
    for item in result.get("trace_evidence", []) + result.get("rag_evidence", []):
        key = (item.get("artifact_id"), item.get("excerpt"))
        if key in seen:
            continue
        seen.add(key)
        evidence.append(Evidence(**item))

    return QueryResponse(
        question=req.question,
        analysis_type=result["analysis_type"],
        answer=result.get("answer", ""),
        findings=[Finding(**f) for f in result.get("deterministic_findings", [])],
        evidence=evidence[:30],
        ragflow_used=result.get("ragflow_used", False),
    )
