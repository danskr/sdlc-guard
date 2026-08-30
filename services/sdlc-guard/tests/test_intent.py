from sdlc_guard.intent import classify


def test_intents():
    assert classify("Which requirements have no test coverage?") == "test_coverage"
    assert classify("Which functionalities are not implemented?") == "implementation_coverage"
    assert classify("Do you see inconsistencies in project scope?") == "consistency"
    assert classify("Is checkout ready for release?") == "release_readiness"
