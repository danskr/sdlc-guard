SHELL := /bin/bash
AGENT_IMAGE ?= sdlc-guard:0.1.0
BACKEND_IMAGE ?= ecommerce-backend:0.1.0
FRONTEND_IMAGE ?= ecommerce-frontend:0.1.0

.PHONY: build test images import-images deploy status port-forward ingest smoke clean

build:
	python3 -m compileall services/sdlc-guard/src sample-project/ecommerce/backend/app

test:
	cd services/sdlc-guard && python3 -m pytest -q

images:
	docker build -f services/sdlc-guard/Dockerfile -t $(AGENT_IMAGE) .
	docker build -t $(BACKEND_IMAGE) sample-project/ecommerce/backend
	docker build -t $(FRONTEND_IMAGE) sample-project/ecommerce/frontend

import-images:
	./scripts/import-images-containerd.sh $(AGENT_IMAGE) $(BACKEND_IMAGE) $(FRONTEND_IMAGE)

deploy:
	kubectl apply -k k8s/base

status:
	kubectl -n sdlc-guard get pods,svc,pvc

ingest:
	./scripts/run-ingestion-job.sh

smoke:
	./scripts/smoke-test.sh

clean:
	kubectl delete namespace sdlc-guard --ignore-not-found
