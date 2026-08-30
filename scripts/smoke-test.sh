#!/usr/bin/env bash
set -euo pipefail
TMP=/tmp/sdlc-guard-port-forward.log
kubectl -n sdlc-guard port-forward svc/sdlc-guard 18080:8080 >"$TMP" 2>&1 &
PF=$!
trap 'kill $PF >/dev/null 2>&1 || true' EXIT
sleep 3

echo "== Health =="
curl -fsS http://127.0.0.1:18080/health | jq .

echo "== Test coverage query =="
curl -fsS -X POST http://127.0.0.1:18080/api/v1/query \
  -H 'Content-Type: application/json' \
  -d '{"question":"Are there any approved functionalities not covered by test implementation?"}' | jq .

echo "== Inconsistency query =="
curl -fsS -X POST http://127.0.0.1:18080/api/v1/query \
  -H 'Content-Type: application/json' \
  -d '{"question":"Do you see any inconsistencies in the current scope of the project?"}' | jq .
