#!/usr/bin/env python3
from pathlib import Path
import sys, yaml

root = Path(__file__).resolve().parents[1]
art_root = root / "artifacts"
docs = []
for p in art_root.rglob("*.yaml"):
    if p.name in {"manifest.yaml", "expected_findings.yaml"}: continue
    d = yaml.safe_load(p.read_text())
    if isinstance(d, dict) and d.get("artifact_id"):
        d["_file"] = p
        docs.append(d)
ids = {d["artifact_id"] for d in docs}
errors=[]
for d in docs:
    for rel, targets in (d.get("relationships") or {}).items():
        if isinstance(targets, str): targets=[targets]
        for t in targets:
            if t not in ids: errors.append(f"{d['artifact_id']} {rel} -> missing {t}")
    if d.get("source_path") and not (root / d["source_path"]).exists():
        errors.append(f"{d['artifact_id']} source_path missing: {d['source_path']}")
if errors:
    print("Artifact validation FAILED")
    print("\n".join(errors))
    sys.exit(1)
print(f"Artifact validation OK: {len(docs)} artifacts, {sum(len(v if isinstance(v,list) else [v]) for d in docs for v in (d.get('relationships') or {}).values())} relationships")
