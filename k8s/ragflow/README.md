# RAGFlow deployment

This project uses the official RAGFlow Helm chart from the upstream RAGFlow repository, pinned to v0.26.4. The helper script `scripts/install-ragflow.sh` clones that release and installs `./helm` into namespace `ragflow` using `values-sdlc-guard.yaml`.

After RAGFlow starts, port-forward its service and configure an OpenAI model provider plus an embedding model in the RAGFlow UI. Then create an API key and place it in the `sdlc-guard-secrets` Kubernetes Secret. The ingestion job will create and populate the dataset automatically.
