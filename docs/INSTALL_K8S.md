# Install, Build, Deploy, Run, and Test on Ubuntu Kubernetes

This procedure assumes an x86-64 Ubuntu VM with a working Kubernetes cluster and `kubectl` access. Everything runs in Kubernetes except Docker, which is used only to build the four local project images before importing them into the cluster's containerd image store.

## 0. VM sizing

RAGFlow upstream documents a minimum of 4 CPU cores, 16 GB RAM, and 50 GB disk for RAGFlow itself. For this all-in-one VM deployment, use approximately:

- 8 vCPU or more
- 24-32 GB RAM
- 80 GB or more free disk

The project uses RAGFlow v0.26.4 and its official Helm chart.

## 1. Unzip and enter the project

```bash
unzip sdlc-guard.zip
cd sdlc-guard
```

## 2. Install host-side build/deployment dependencies

If `kubectl` and your Kubernetes cluster already work, do not reinstall Kubernetes.

```bash
sudo apt update
sudo apt install -y git curl jq unzip ca-certificates gnupg
```

Install Helm if it is not already present:

```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
helm version
```

Install/start Docker Engine if Docker is not already usable:

```bash
sudo apt install -y docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
```

Log out and back in once after changing Docker group membership, or run Docker with `sudo` for the current shell.

Check all prerequisites:

```bash
./scripts/check-prereqs.sh
```

## 3. Ensure Kubernetes has a default StorageClass

Check:

```bash
kubectl get storageclass
```

If one is already marked `(default)`, skip this step.

For a single-node lab cluster without dynamic storage, install Rancher local-path-provisioner:

```bash
./scripts/install-local-path-provisioner.sh
```

The script pins v0.0.36 and marks its `local-path` StorageClass as default.

## 4. Compile/static-check the supplied Python source

From the project root:

```bash
python3 -m compileall services/sdlc-guard/src sample-project/ecommerce/backend/app
```

The production dependencies are installed inside the Docker images, so a host Python virtual environment is not required for deployment.

Optional local unit tests:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e 'services/sdlc-guard[test]'
pytest -q services/sdlc-guard/tests
```

## 5. Install RAGFlow in Kubernetes

RAGFlow requires `vm.max_map_count >= 262144`. The installer sets and persists this value when necessary.

```bash
./scripts/install-ragflow.sh
```

Watch startup:

```bash
kubectl -n ragflow get pods -w
```

Inspect all RAGFlow resources:

```bash
kubectl -n ragflow get pods,svc,pvc
```

## 6. Open RAGFlow and configure model access

Start a port-forward:

```bash
kubectl -n ragflow port-forward svc/ragflow 9380:80
```

Open:

```text
http://localhost:9380
```

Create/sign in to the local RAGFlow user.

In RAGFlow:

1. Open the user/avatar settings.
2. Open **Model providers**.
3. Configure OpenAI using your OpenAI API key.
4. Add/select a chat model and an embedding model.
5. In System Model Settings, set the default embedding model. This must be done before the ingestion job creates/parses the dataset.
6. Click your avatar -> **API** and create/copy a RAGFlow API key.

The RAGFlow API key is different from your OpenAI API key.

## 7. Export the two keys and create the Kubernetes Secret

In a shell (do not put real keys into Git):

```bash
export OPENAI_API_KEY='YOUR_OPENAI_API_KEY'
export RAGFLOW_API_KEY='YOUR_RAGFLOW_API_KEY'
./scripts/create-secrets.sh
```

Verify only the secret name, not the secret value:

```bash
kubectl -n sdlc-guard get secret sdlc-guard-secrets
```

## 8. Build all project images

```bash
./scripts/build-images.sh
```

This builds:

- `sdlc-guard:0.1.0`
- `sdlc-guard-ui:0.1.0`
- `ecommerce-backend:0.1.0`
- `ecommerce-frontend:0.1.0`

The TypeScript frontend is compiled during its multi-stage Docker build using `tsc` and Vite.

## 9. Import local images into Kubernetes/containerd

A kubeadm/containerd cluster does not automatically see images built in Docker's image store. Import them:

```bash
./scripts/import-images-containerd.sh
```

Confirm:

```bash
sudo ctr -n k8s.io images list | grep -E 'sdlc-guard|ecommerce-backend|ecommerce-frontend'
```

## 10. Deploy SDLC-Guard and the demo e-commerce app

```bash
./scripts/deploy-sdlc-guard.sh
```

Expected namespace resources:

```bash
kubectl -n sdlc-guard get pods,svc,pvc
```

You should have running pods for:

- `traceability-postgres`
- `sdlc-guard`
- `sdlc-guard-ui`
- `ecommerce-backend`
- `ecommerce-frontend`

## 11. Import the SDLC corpus into PostgreSQL and RAGFlow

Run:

```bash
./scripts/run-ingestion-job.sh
```

The ingestion container does two things:

1. Rebuilds the PostgreSQL traceability model from the YAML artifacts.
2. Creates/recreates the RAGFlow dataset `sdlc-guard-ecommerce-demo`, uploads every artifact, and triggers parsing/embedding.

For source/test artifacts, the generated RAG document also embeds the actual connected source file content.

Inspect the job later with:

```bash
kubectl -n sdlc-guard logs job/sdlc-guard-ingest
```

## 12. Open SDLC-Guard and demo app

In terminal 1:

```bash
kubectl -n sdlc-guard port-forward svc/sdlc-guard 8080:8080
```

In terminal 2:

```bash
kubectl -n sdlc-guard port-forward svc/ecommerce-frontend 8088:80
```

In terminal 3:

```bash
kubectl -n sdlc-guard port-forward svc/sdlc-guard-ui 3000:80
```

Open:

- SDLC-Guard Swagger UI: `http://localhost:8080/docs`
- SDLC-Guard Web UI: `http://localhost:3000`
- Demo e-commerce UI: `http://localhost:8088`

## 13. Test the demo e-commerce backend

```bash
kubectl -n sdlc-guard port-forward svc/ecommerce-backend 8081:8081
```

Then:

```bash
curl -s http://localhost:8081/health | jq .
```

Successful card checkout:

```bash
curl -s -X POST http://localhost:8081/api/v1/checkout \
  -H 'Content-Type: application/json' \
  -H 'X-User-Id: demo-user' \
  -d '{
    "cart_id":"cart-100",
    "payment_method":"card",
    "amount":42.50,
    "idempotency_key":"demo-idempotency-1"
  }' | jq .
```

Try the same idempotency key twice. The demo intentionally fails to enforce idempotency; that mismatch is one of SDLC-Guard's seeded findings.

## 14. Ask SDLC-Guard questions

Health:

```bash
curl -s http://localhost:8080/health | jq .
```

Test gaps:

```bash
curl -s -X POST http://localhost:8080/api/v1/query \
  -H 'Content-Type: application/json' \
  -d '{"question":"Are there any approved functionalities not covered by test implementation?"}' | jq .
```

Implementation gaps:

```bash
curl -s -X POST http://localhost:8080/api/v1/query \
  -H 'Content-Type: application/json' \
  -d '{"question":"Are there any functionalities that are not implemented at all and have no source code counterpart?"}' | jq .
```

Scope inconsistencies:

```bash
curl -s -X POST http://localhost:8080/api/v1/query \
  -H 'Content-Type: application/json' \
  -d '{"question":"Do you see any inconsistencies in the current scope of the project?"}' | jq .
```

Broad gap analysis:

```bash
curl -s -X POST http://localhost:8080/api/v1/query \
  -H 'Content-Type: application/json' \
  -d '{"question":"What are the missing pieces in the current project scope?"}' | jq .
```

NFR analysis:

```bash
curl -s -X POST http://localhost:8080/api/v1/query \
  -H 'Content-Type: application/json' \
  -d '{"question":"Which non-functional requirements have not been verified?"}' | jq .
```

Release readiness:

```bash
curl -s -X POST http://localhost:8080/api/v1/query \
  -H 'Content-Type: application/json' \
  -d '{"question":"Is checkout ready for release?"}' | jq .
```

Or run the included smoke suite while SDLC-Guard is deployed:

```bash
./scripts/smoke-test.sh
```

## 15. Compare results with known ground truth

Read:

```bash
cat docs/DEMO_GROUND_TRUTH.md
```

The most important expected findings include guest/auth contradiction, idempotency implementation gap, wallet reserve/capture mismatch, missing partial refund implementation, orphan promotion code, and unverified performance/audit NFRs.

## 16. Troubleshooting

### Pod is ImagePullBackOff

Confirm local images are in containerd:

```bash
sudo ctr -n k8s.io images list | grep -E 'sdlc-guard|ecommerce'
```

Re-run:

```bash
./scripts/import-images-containerd.sh
kubectl -n sdlc-guard rollout restart deployment/sdlc-guard deployment/ecommerce-backend deployment/ecommerce-frontend
```

### PVC is Pending

```bash
kubectl get storageclass
kubectl -n sdlc-guard describe pvc traceability-postgres-data
kubectl -n ragflow get pvc
```

If there is no default StorageClass:

```bash
./scripts/install-local-path-provisioner.sh
```

### RAGFlow retrieval fails

Check:

```bash
kubectl -n ragflow get pods
kubectl -n sdlc-guard logs deployment/sdlc-guard
kubectl -n sdlc-guard logs job/sdlc-guard-ingest
```

Confirm the RAGFlow OpenAI provider/default embedding model is configured and that the RAGFlow API key is valid.

### Re-ingest after editing artifacts

Rebuild the SDLC-Guard image because it contains the corpus:

```bash
docker build -f services/sdlc-guard/Dockerfile -t sdlc-guard:0.1.0 .
./scripts/import-images-containerd.sh sdlc-guard:0.1.0
kubectl -n sdlc-guard rollout restart deployment/sdlc-guard
./scripts/run-ingestion-job.sh
```

## 17. Remove the project

```bash
kubectl delete namespace sdlc-guard
helm uninstall ragflow -n ragflow
kubectl delete namespace ragflow
```

Remove the local-path provisioner only if nothing else in your cluster uses it.
