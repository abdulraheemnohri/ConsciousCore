from app.runtime.policy import classify
from app.runtime.router import RuntimeRouter
from app.runtime.types import RuntimeMode, RuntimeRequest


def test_secret_is_never_cloud_allowed():
    decision = classify("api_key=super-secret-value", "private")
    assert decision.classification == "secret"
    assert decision.cloud_allowed is False


def test_auto_defaults_to_local_when_remote_is_disabled():
    router = RuntimeRouter()
    result = router.choose(RuntimeRequest(prompt="hello", mode=RuntimeMode.AUTO))
    assert result[0].provider == "local"


def test_hybrid_can_add_cloud_only_when_policy_allows():
    router = RuntimeRouter()
    router.register_provider("cloud", enabled=True, models=["cloud-model"])
    request = RuntimeRequest(
        prompt="summarize public documentation",
        mode=RuntimeMode.HYBRID,
        privacy="public",
        allow_cloud=True,
    )
    result = router.choose(request)
    assert [r.provider for r in result] == ["local", "cloud"]


def test_parallel_returns_enabled_allowed_candidates():
    router = RuntimeRouter()
    router.register_provider("remote", enabled=True, models=["remote-model"])
    request = RuntimeRequest(
        prompt="public task",
        mode=RuntimeMode.PARALLEL,
        privacy="public",
        allow_remote=True,
        candidates=["local", "remote"],
    )
    result = router.choose(request)
    assert {r.provider for r in result} == {"local", "remote"}
