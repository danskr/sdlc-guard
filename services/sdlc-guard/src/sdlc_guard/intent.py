from .models import AnalysisType


def classify(question: str) -> AnalysisType:
    q = question.lower()

    if "ready for release" in q or "release readiness" in q:
        return "release_readiness"

    if (
        "code" in q
        or "source" in q
        or "implementation" in q
    ) and (
        "without requirement" in q
        or "without an approved requirement" in q
        or "no approved requirement" in q
        or "has no approved requirement" in q
        or "not traceable to approved" in q
        or "not traceable to scope" in q
        or "unapproved implementation" in q
        or "orphan" in q
    ):
        return "orphan_implementation"

    if (
        "impact" in q
        or "affected" in q
        or "remove" in q
        or "change" in q
    ):
        return "change_impact"

    if (
        "nfr" in q
        or "non-functional" in q
        or "performance" in q
        or "security requirement" in q
    ):
        return "nfr_coverage"

    if "not covered" in q and (
        "test" in q or "test case" in q
    ):
        return "test_coverage"

    if (
        "without test" in q
        or "no test" in q
        or "test coverage" in q
    ):
        return "test_coverage"

    if (
        "not implemented" in q
        or "no source" in q
        or "no code" in q
        or "implementation coverage" in q
    ):
        return "implementation_coverage"

    if (
        "inconsisten" in q
        or "contradict" in q
        or "conflict" in q
    ):
        return "consistency"

    if (
        "gap" in q
        or "missing" in q
        or "scope" in q
    ):
        return "gaps"

    return "general"
