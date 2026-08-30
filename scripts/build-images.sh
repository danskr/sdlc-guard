#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

docker build -f services/sdlc-guard/Dockerfile -t sdlc-guard:0.1.0 .
docker build -t sdlc-guard-ui:0.1.0 services/sdlc-guard-ui
docker build -t ecommerce-backend:0.1.0 sample-project/ecommerce/backend
docker build -t ecommerce-frontend:0.1.0 sample-project/ecommerce/frontend

docker images | grep -E 'sdlc-guard|sdlc-guard-ui|ecommerce-backend|ecommerce-frontend' || true
