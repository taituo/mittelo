from src.wrapper.prereqs import preflight_backend


def test_preflight_echo_ok() -> None:
    res = preflight_backend("echo")
    assert res.status == "ok"


def test_preflight_unknown_backend_fails() -> None:
    res = preflight_backend("no_such_backend_123")
    assert res.status == "fail"
    assert res.problems


def test_preflight_opencode_fails() -> None:
    res = preflight_backend("opencode")
    assert res.status == "fail"
    assert res.problems

