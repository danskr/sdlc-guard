from types import SimpleNamespace

import pytest

import sdlc_guard.ragflow as ragflow_module
from sdlc_guard.intent import classify
from sdlc_guard.ragflow import RAGFlowClient


def make_client():
    client = RAGFlowClient.__new__(RAGFlowClient)

    client.settings = SimpleNamespace(
        ragflow_api_key="test-key",
        ragflow_required=True,
        ragflow_dataset_id="dataset-123",
        ragflow_dataset_name="sdlc-guard-ecommerce-demo",
        ragflow_base_url="http://ragflow.test",
        retrieval_size=5,
        similarity_threshold=0.2,
        vector_similarity_weight=0.3,
    )

    return client


def test_orphan_implementation_natural_language():
    assert (
        classify("Is there source code that has no approved requirement?")
        == "orphan_implementation"
    )

    assert (
        classify("Find orphan implementations")
        == "orphan_implementation"
    )

    assert (
        classify("Is any code not traceable to approved scope?")
        == "orphan_implementation"
    )


def test_not_implemented_still_classifies_as_implementation_coverage():
    assert (
        classify("Are there functionalities that are not implemented?")
        == "implementation_coverage"
    )


def test_ragflow_uses_public_retrieval_endpoint(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "code": 0,
                "data": {
                    "chunks": [
                        {
                            "document_name": "TECH-PAYMENT-002.md",
                            "content": "Timeout reconciliation evidence",
                            "similarity": 0.91,
                        }
                    ]
                },
            }

    class FakeHTTPClient:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def post(self, url, headers=None, json=None):
            captured["url"] = url
            captured["headers"] = headers
            captured["json"] = json
            return FakeResponse()

    monkeypatch.setattr(
        ragflow_module.httpx,
        "Client",
        lambda timeout=60: FakeHTTPClient(),
    )

    client = make_client()
    result = client.search("payment gateway timeout reconciliation")

    assert captured["url"] == "http://ragflow.test/api/v1/retrieval"
    assert captured["json"]["dataset_ids"] == ["dataset-123"]
    assert captured["json"]["page_size"] == 5
    assert "size" not in captured["json"]

    assert len(result) == 1
    assert result[0]["source"] == "ragflow"
    assert result[0]["artifact_id"] == "TECH-PAYMENT-002.md"


def test_ragflow_application_error_is_not_silently_ignored(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "code": 100,
                "message": "embedding provider unavailable",
            }

    class FakeHTTPClient:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def post(self, url, headers=None, json=None):
            return FakeResponse()

    monkeypatch.setattr(
        ragflow_module.httpx,
        "Client",
        lambda timeout=60: FakeHTTPClient(),
    )

    client = make_client()

    with pytest.raises(
        RuntimeError,
        match="RAGFlow retrieval failed",
    ):
        client.search("payment gateway timeout reconciliation")
