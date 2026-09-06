from app.runtime.policy import classify
from app.runtime.router import RuntimeRouter
from app.runtime.types import RuntimeMode, RuntimeRequest


def test_secret_is_never_cloud_allowed_and_is_redacted():
    decision = classify("api_key=super-secret-value", "private")
    assert decision.classification == "secret"
    assert decision.cloud_allowed is False
    assert decision.remote_allowed is False
    assert "super-secret-value" not in decision.redacted_prompt


def test_auto_defaults_to_local_when_remote_is_disabled():
    router = RuntimeRouter()
    result = router.choose(RuntimeRequest(prompt="hello", mode=RuntimeMode.AUTO))
    assert result[0].provider == "local"


def test_hybrid_selects_remote_generator_when_local_is_not_a_remote_route():
    router = RuntimeRouter()
    router.register_provider("cloud", enabled=True, models=["cloud-model"])
    request = RuntimeRequest(prompt="summarize public documentation", mode=RuntimeMode.HYBRID, privacy="public", allow_cloud=True)
    result = router.choose(request)
    assert [r.provider for r in result] == ["local", "cloud"]


def test_parallel_returns_enabled_allowed_candidates():
    router = RuntimeRouter()
    router.register_provider("remote", enabled=True, models=["remote-model"])
    request = RuntimeRequest(prompt="public task", mode=RuntimeMode.PARALLEL, privacy="public", allow_remote=True, candidates=["local", "remote"])
    result = router.choose(request)
    assert {r.provider for r in result} == {"local", "remote"}


def test_sensitive_data_blocks_cloud_and_remote():
    router = RuntimeRouter()
    router.register_provider("cloud", enabled=True, models=["cloud-model"])
    router.register_provider("remote", enabled=True, models=["remote-model"])
    request = RuntimeRequest(prompt="private account number 1234567890123456", mode=RuntimeMode.PARALLEL, privacy="sensitive", allow_cloud=True, allow_remote=True, candidates=["cloud", "remote"])
    result = router.choose(request)
    assert [r.provider for r in result] == ["local"]
