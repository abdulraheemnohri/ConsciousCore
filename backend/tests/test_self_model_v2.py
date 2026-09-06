from app.core.self_model_v2 import SelfModelEngine


def test_self_model_defaults_are_explicit():
    model = SelfModelEngine().snapshot()
    assert model["name"] == "ConsciousCore"
    assert model["scientifically_conscious"] is False
    assert model["local_only"] is True
    assert model["autonomy_level"] == 1
    assert model["capabilities"]
    assert model["limitations"]
    assert model["boundaries"]


def test_self_model_role_and_autonomy_persist():
    model = SelfModelEngine()
    result = model.update_role("local research runtime", 2)
    assert result["role"] == "local research runtime"
    assert result["autonomy_level"] == 2
    reloaded = SelfModelEngine().snapshot()
    assert reloaded["role"] == "local research runtime"
    assert reloaded["autonomy_level"] == 2


def test_self_model_autonomy_is_clamped():
    model = SelfModelEngine()
    assert model.update_role(autonomy_level=99)["autonomy_level"] == 3
    assert model.update_role(autonomy_level=-5)["autonomy_level"] == 0


def test_self_model_assess_reports_runtime():
    model = SelfModelEngine()
    result = model.assess(model_backend="fallback", memory_count=4, active_goals=2)
    assert result["runtime"] == {"model_backend": "fallback", "memory_records": 4, "active_goals": 2, "ready": True}
