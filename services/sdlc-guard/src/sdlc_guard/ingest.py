from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

import httpx
import yaml
from sqlalchemy import delete

from .config import get_settings
from .db import Artifact, ArtifactRelationship, Base, SessionLocal, engine


def load_documents(root: Path):
    docs = []
    for path in sorted(root.rglob("*.yaml")):
        if path.name in {"manifest.yaml", "expected_findings.yaml"}:
            continue
        data = yaml.safe_load(path.read_text())
        if not isinstance(data, dict) or "artifact_id" not in data:
            continue
        data["_path"] = str(path)
        docs.append(data)
    return docs


def render_markdown(doc: dict, workspace: Path) -> bytes:
    rels = doc.get("relationships", {}) or {}
    lines = [
        f"# {doc['artifact_id']} - {doc.get('title','')}", "",
        f"Artifact type: {doc.get('artifact_type')}",
        f"Project: {doc.get('project_id')}",
        f"Feature: {doc.get('feature_id','')}",
        f"Status: {doc.get('status','approved')}", "",
        "## Content", "", doc.get("content", ""), "", "## Relationships", "",
    ]
    for relation, targets in rels.items():
        if isinstance(targets, str): targets = [targets]
        lines.append(f"- {relation}: {', '.join(targets)}")
    if doc.get("source_path"):
        lines += ["", f"Source path: `{doc['source_path']}`"]
    if doc.get("source_path"):
        source_file = workspace / doc["source_path"]
        if source_file.exists() and source_file.is_file():
            lines += ["", "## Connected source/test implementation", "", "```", source_file.read_text(errors="replace"), "```"]
    return ("\n".join(lines) + "\n").encode()


def seed_traceability(docs: list[dict]):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        session.execute(delete(ArtifactRelationship))
        session.execute(delete(Artifact))
        for d in docs:
            session.add(Artifact(
                artifact_id=d["artifact_id"], project_id=d.get("project_id", "ecommerce-demo"),
                artifact_type=d["artifact_type"], title=d.get("title", d["artifact_id"]),
                content=d.get("content", ""), status=d.get("status", "approved"),
                feature_id=d.get("feature_id"), source_path=d.get("source_path"), version=str(d.get("version", "1")),
            ))
        session.flush()
        ids = {d["artifact_id"] for d in docs}
        for d in docs:
            for rel_type, targets in (d.get("relationships") or {}).items():
                if isinstance(targets, str): targets = [targets]
                for target in targets:
                    if target not in ids:
                        print(f"WARN relationship target not found: {d['artifact_id']} {rel_type} {target}")
                        continue
                    session.add(ArtifactRelationship(source_id=d["artifact_id"], relation_type=rel_type, target_id=target))
        session.commit()
    print(f"Seeded {len(docs)} artifacts into traceability PostgreSQL")


def rag_headers(key):
    return {"Authorization": f"Bearer {key}"}


def ragflow_import(docs: list[dict], workspace: Path, recreate: bool = True):
    s = get_settings()
    if not s.ragflow_api_key:
        raise RuntimeError("RAGFLOW_API_KEY is required for RAGFlow import")
    base = s.ragflow_base_url.rstrip("/")
    headers = rag_headers(s.ragflow_api_key)
    with httpx.Client(timeout=120) as client:
        r = client.get(f"{base}/api/v1/datasets", headers=headers, params={"name": s.ragflow_dataset_name})
        r.raise_for_status()
        payload = r.json().get("data") or []
        if isinstance(payload, dict): payload = payload.get("datasets") or []
        existing = next((x for x in payload if x.get("name") == s.ragflow_dataset_name), None)
        if existing and recreate:
            dr = client.request("DELETE", f"{base}/api/v1/datasets", headers={**headers, "Content-Type": "application/json"}, json={"ids": [existing["id"]]})
            dr.raise_for_status(); existing = None
        if existing:
            dataset_id = existing["id"]
        else:
            cr = client.post(f"{base}/api/v1/datasets", headers={**headers, "Content-Type": "application/json"}, json={
                "name": s.ragflow_dataset_name,
                "description": "SDLC-Guard e-commerce demo corpus with deliberately seeded SDLC gaps and inconsistencies.",
                "chunk_method": "naive",
            })
            cr.raise_for_status()
            dataset_id = cr.json()["data"]["id"]
        print(f"Using RAGFlow dataset {s.ragflow_dataset_name} ({dataset_id})")

        uploaded = []
        for d in docs:
            name = f"{d['artifact_id']}.md"
            files = {"file": (name, render_markdown(d, workspace), "text/markdown")}
            ur = client.post(f"{base}/api/v1/datasets/{dataset_id}/documents", headers=headers, files=files)
            ur.raise_for_status()
            body = ur.json()
            if body.get("code") not in (0, None):
                raise RuntimeError(body)
            uploaded.extend(x["id"] for x in body.get("data", []))
        print(f"Uploaded {len(uploaded)} documents to RAGFlow")

        if uploaded:
            pr = client.post(f"{base}/api/v1/datasets/{dataset_id}/chunks", headers={**headers, "Content-Type": "application/json"}, json={"document_ids": uploaded})
            pr.raise_for_status()
            if pr.json().get("code") not in (0, None): raise RuntimeError(pr.json())
            print("Started RAGFlow parsing/embedding. Waiting for completion...")
            deadline = time.time() + 1200
            while time.time() < deadline:
                lr = client.get(f"{base}/api/v1/datasets/{dataset_id}/documents", headers=headers, params={"page_size": 100})
                lr.raise_for_status()
                data = lr.json().get("data") or {}
                current = data.get("docs") if isinstance(data, dict) else data
                current = current or []
                pending = [x for x in current if x.get("id") in uploaded and str(x.get("run", "")).upper() not in {"DONE", "3", "4", "FAIL", "CANCEL"} and float(x.get("progress") or 0) < 1]
                if not pending:
                    print("RAGFlow parsing is complete (or in terminal state).")
                    return dataset_id
                print(f"  {len(pending)} documents still parsing...")
                time.sleep(5)
            raise TimeoutError("Timed out waiting for RAGFlow document parsing")
    return dataset_id


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts", default=os.getenv("ARTIFACTS_DIR", "/workspace/artifacts"))
    parser.add_argument("--workspace", default=os.getenv("WORKSPACE_DIR", "/workspace"))
    parser.add_argument("--skip-ragflow", action="store_true")
    parser.add_argument("--keep-dataset", action="store_true")
    args = parser.parse_args()
    docs = load_documents(Path(args.artifacts))
    if not docs:
        raise SystemExit(f"No artifact YAML files found below {args.artifacts}")
    seed_traceability(docs)
    if not args.skip_ragflow:
        dataset_id = ragflow_import(docs, Path(args.workspace), recreate=not args.keep_dataset)
        print(f"RAGFLOW_DATASET_ID={dataset_id}")


if __name__ == "__main__":
    main()
