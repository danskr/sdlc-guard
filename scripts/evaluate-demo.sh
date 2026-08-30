#!/usr/bin/env bash
set -euo pipefail
BASE="${SDLC_AGENT_URL:-http://127.0.0.1:8080}"
questions=(
  "Do you see any inconsistencies in the current scope of the project?"
  "Are there any approved functionalities not covered by test implementation?"
  "Are there any functionalities that are not implemented at all and have no source code counterpart?"
  "Is there source code that has no approved requirement?"
  "Which non-functional requirements have not been verified?"
  "Is checkout ready for release?"
)
for q in "${questions[@]}"; do
  echo
  echo "### $q"
  curl -fsS -X POST "$BASE/api/v1/query" -H 'Content-Type: application/json' \
    -d "$(jq -cn --arg q "$q" '{question:$q}')" | jq '{analysis_type,answer,findings,ragflow_used}'
done
