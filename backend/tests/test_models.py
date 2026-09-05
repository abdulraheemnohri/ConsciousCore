from pathlib import Path

from app.core.engine import CognitiveEngine
from app.models.fallback import FallbackModel
from app.models.manager import ModelManager


def test_model_manager_discovers_gguf(tmp_path: Path):
    (tmp_path / "demo.gguf").write_bytes(b"")
    manager = ModelManager(str(tmp_path))
    found = manager.discover_gguf()
    assert found == ["demo"]
    assert manager.list()["active"] == "demo"
    assert manager.list()["models"][0]["backend"] == "llama.cpp"


def test_engine_uses_fallback_when_no_local_model_exists(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    engine = CognitiveEngine()
    assert isinstance(engine.model, FallbackModel)


def test_engine_can_activate_registered_model(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("models").mkdir()
    Path("models/demo.gguf").write_bytes(b"")
    engine = CognitiveEngine()
    assert engine.model_manager.list()["active"] == "demo"
    assert engine.model.info()["backend"] == "llama.cpp"
