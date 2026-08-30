#!/usr/bin/env bash
set -euo pipefail
cat <<'TXT'
Run these in separate terminals:

  kubectl -n sdlc-guard port-forward svc/sdlc-guard 8080:8080
  kubectl -n sdlc-guard port-forward svc/ecommerce-frontend 8088:80
  kubectl -n ragflow port-forward svc/ragflow 9380:80

Then use:
  SDLC-Guard API/docs: http://localhost:8080/docs
  Demo e-commerce UI:  http://localhost:8088
  RAGFlow UI:          http://localhost:9380
TXT
