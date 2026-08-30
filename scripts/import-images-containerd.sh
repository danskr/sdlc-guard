#!/usr/bin/env bash
set -euo pipefail

if [[ $# -eq 0 ]]; then
  IMAGES=(
    sdlc-guard:0.1.0
    sdlc-guard-ui:0.1.0
    ecommerce-backend:0.1.0
    ecommerce-frontend:0.1.0
  )
else
  IMAGES=("$@")
fi

for image in "${IMAGES[@]}"; do
  safe="${image//[:\//]/_}"
  tar="/tmp/${safe}.tar"
  echo "Exporting $image -> $tar"
  docker save "$image" -o "$tar"
  echo "Importing $image into containerd k8s.io namespace"
  sudo ctr -n k8s.io images import "$tar"
  rm -f "$tar"
done

sudo ctr -n k8s.io images list | grep -E 'sdlc-guard|sdlc-guard-ui|ecommerce-backend|ecommerce-frontend' || true
