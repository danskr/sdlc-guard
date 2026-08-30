#!/usr/bin/env bash
set -euo pipefail

if kubectl get storageclass -o json | jq -e '.items[] | select(.metadata.annotations["storageclass.kubernetes.io/is-default-class"]=="true")' >/dev/null; then
  echo "A default StorageClass already exists; no change made."
  kubectl get storageclass
  exit 0
fi

echo "Installing Rancher local-path-provisioner v0.0.36..."
kubectl apply -f https://raw.githubusercontent.com/rancher/local-path-provisioner/v0.0.36/deploy/local-path-storage.yaml
kubectl -n local-path-storage rollout status deployment/local-path-provisioner --timeout=180s

kubectl patch storageclass local-path -p '{"metadata":{"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
echo "Default StorageClass:"
kubectl get storageclass
