from sdlc_guard.models import QueryRequest


def test_query_request_defaults():
    req = QueryRequest(question="Find missing test coverage")
    assert req.project_id == "ecommerce-demo"
