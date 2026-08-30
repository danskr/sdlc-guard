#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VERSION="${RAGFLOW_VERSION:-v0.26.4}"
WORK="${RAGFLOW_SOURCE_DIR:-$HOME/ragflow-${VERSION}}"

if [[ "$(sysctl -n vm.max_map_count)" -lt 262144 ]]; then
  echo "Setting vm.max_map_count=262144 for RAGFlow..."
  sudo sysctl -w vm.max_map_count=262144
  if ! grep -q '^vm.max_map_count=262144' /etc/sysctl.conf 2>/dev/null; then
    echo 'vm.max_map_count=262144' | sudo tee -a /etc/sysctl.conf >/dev/null
  fi
fi

if ! kubectl get storageclass -o json | jq -e '.items[] | select(.metadata.annotations["storageclass.kubernetes.io/is-default-class"]=="true")' >/dev/null; then
  echo "ERROR: no default Kubernetes StorageClass. Run ./scripts/install-local-path-provisioner.sh first."
  exit 1
fi

if [[ ! -d "$WORK/.git" ]]; then
  git clone --depth 1 --branch "$VERSION" https://github.com/infiniflow/ragflow.git "$WORK"
else
  git -C "$WORK" fetch --tags --depth 1 origin "$VERSION"
  git -C "$WORK" checkout "$VERSION"
fi

helm upgrade --install ragflow "$WORK/helm" \
  --namespace ragflow --create-namespace \
  -f "$ROOT/k8s/ragflow/values-sdlc-guard.yaml"

echo
kubectl -n ragflow get pods,svc,pvc
echo
cat <<'TXT'
RAGFlow has been submitted to Kubernetes.
Wait until its pods are Ready. You can watch with:
  kubectl -n ragflow get pods -w

Then expose the UI locally:
  kubectl -n ragflow port-forward svc/ragflow 9380:80

Open http://localhost:9380 from a browser running on the Ubuntu VM, or use SSH/VM port forwarding from the host machine.
TXT
