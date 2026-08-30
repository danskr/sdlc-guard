#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

kubectl apply -k "$ROOT/k8s/base"
kubectl -n sdlc-guard rollout status deployment/traceability-postgres --timeout=180s
kubectl -n sdlc-guard rollout status deployment/ecommerce-backend --timeout=180s
kubectl -n sdlc-guard rollout status deployment/ecommerce-frontend --timeout=180s
kubectl -n sdlc-guard rollout status deployment/sdlc-guard --timeout=180s
kubectl -n sdlc-guard rollout status deployment/sdlc-guard-ui --timeout=180s
kubectl -n sdlc-guard get pods,svc,pvc
