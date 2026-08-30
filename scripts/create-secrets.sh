#!/usr/bin/env bash
set -euo pipefail

: "${OPENAI_API_KEY:?Set OPENAI_API_KEY in the shell before running this script}"
: "${RAGFLOW_API_KEY:?Set RAGFLOW_API_KEY in the shell before running this script}"

kubectl create namespace sdlc-guard --dry-run=client -o yaml | kubectl apply -f -
kubectl -n sdlc-guard create secret generic sdlc-guard-secrets \
  --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" \
  --from-literal=RAGFLOW_API_KEY="$RAGFLOW_API_KEY" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Created/updated secret sdlc-guard/sdlc-guard-secrets"
