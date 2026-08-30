#!/usr/bin/env bash
set -euo pipefail

need() { command -v "$1" >/dev/null 2>&1 || { echo "ERROR: $1 is required"; exit 1; }; }
need kubectl
need helm
need docker
need curl
need jq

echo "== Kubernetes =="
kubectl version --client
kubectl get nodes -o wide

echo "== Helm =="
helm version --short

echo "== Docker =="
docker --version

echo "== Storage classes =="
kubectl get storageclass || true

echo "== Host resources =="
echo "CPU: $(nproc)"
free -h || true
df -h / || true

echo "== vm.max_map_count =="
sysctl vm.max_map_count || true

cat <<'TXT'

RAGFlow's upstream quickstart specifies at least 4 CPU cores, 16 GB RAM and 50 GB disk for RAGFlow itself.
For RAGFlow + SDLC-Guard + PostgreSQL + the demo application on one VM, 8 vCPU, 24-32 GB RAM, and 80+ GB free disk is recommended.
TXT
