from __future__ import annotations

import httpx

from .config import get_settings


class RAGFlowClient:
    def __init__(self):
        self.settings = get_settings()

    @property
    def configured(self) -> bool:
        return bool(self.settings.ragflow_api_key)

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.settings.ragflow_api_key}",
            "Content-Type": "application/json",
        }

    def find_dataset_id(self) -> str:
        if self.settings.ragflow_dataset_id:
            return self.settings.ragflow_dataset_id

        with httpx.Client(timeout=30) as client:
            r = client.get(
                f"{self.settings.ragflow_base_url}/api/v1/datasets",
                headers=self._headers(),
                params={"name": self.settings.ragflow_dataset_name},
            )
            r.raise_for_status()

            body = r.json()

            if body.get("code") not in (None, 0):
                raise RuntimeError(
                    f"RAGFlow dataset lookup failed: "
                    f"{body.get('message', 'unknown error')}"
                )

            data = body.get("data") or []

            if isinstance(data, dict):
                data = (
                    data.get("datasets")
                    or data.get("docs")
                    or []
                )

            for ds in data:
                if ds.get("name") == self.settings.ragflow_dataset_name:
                    return ds["id"]

        raise RuntimeError(
            f"RAGFlow dataset "
            f"'{self.settings.ragflow_dataset_name}' not found"
        )

    def search(self, question: str) -> list[dict]:
        if not self.configured:
            if self.settings.ragflow_required:
                raise RuntimeError("RAGFLOW_API_KEY is required")
            return []

        dataset_id = self.find_dataset_id()

        payload = {
            "question": question,
            "dataset_ids": [dataset_id],
            "page": 1,
            "page_size": self.settings.retrieval_size,
            "similarity_threshold": self.settings.similarity_threshold,
            "vector_similarity_weight": self.settings.vector_similarity_weight,
            "top_k": 128,
            "keyword": True,
            "use_kg": False,
        }

        with httpx.Client(timeout=60) as client:
            r = client.post(
                f"{self.settings.ragflow_base_url}/api/v1/retrieval",
                headers=self._headers(),
                json=payload,
            )

            r.raise_for_status()
            body = r.json()

        # RAGFlow can return HTTP 200 with an application-level
        # error code, so check both HTTP and RAGFlow status.
        if body.get("code") not in (None, 0):
            raise RuntimeError(
                f"RAGFlow retrieval failed: "
                f"{body.get('message', 'unknown error')}"
            )

        chunks = (body.get("data") or {}).get("chunks") or []

        out = []

        for c in chunks:
            out.append(
                {
                    "artifact_id": (
                        c.get("document_keyword")
                        or c.get("document_name")
                        or c.get("id", "rag-chunk")
                    ),
                    "artifact_type": "rag_chunk",
                    "title": (
                        c.get("document_name")
                        or c.get("document_keyword")
                        or "RAGFlow evidence"
                    ),
                    "excerpt": (
                        c.get("content_with_weight")
                        or c.get("content")
                        or ""
                    ),
                    "source": "ragflow",
                    "score": c.get("similarity"),
                }
            )

        return out
