#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NS="sdlc-guard"
JOB="sdlc-guard-ingest"

kubectl -n "$NS" delete job "$JOB" --ignore-not-found --wait=true
kubectl apply -f "$ROOT/k8s/jobs/ingest-job.yaml"

echo "Waiting for ingestion pod..."

POD=""
for _ in $(seq 1 120); do
  POD="$(
    kubectl -n "$NS" get pods \
      -l job-name="$JOB" \
      -o jsonpath='{.items[0].metadata.name}' \
      2>/dev/null || true
  )"

  if [[ -n "$POD" ]]; then
    break
  fi

  sleep 1
done

if [[ -z "$POD" ]]; then
  echo "Timed out waiting for ingestion pod."
  kubectl -n "$NS" describe job "$JOB" || true
  exit 1
fi

echo "Following ingestion logs from $POD..."
kubectl -n "$NS" logs -f "$POD"

kubectl -n "$NS" wait \
  --for=condition=complete \
  "job/$JOB" \
  --timeout=1200s

echo "Ingestion completed successfully."
