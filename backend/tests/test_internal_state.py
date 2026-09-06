from pathlib import Path

from app.core.internal_state import InternalStateEngine
from app.database import Database


def test_internal_state_transition_and_status(tmp_path: Path, monkeypatch):
    database = Database(tmp_path / "state.db")
    monkeypatch.setattr("app.core.internal_state.db", database)
    state = InternalStateEngine()
    result = state.observe(input_length=1000, memory_count=8, uncertainty=.8)
    assert result["attention_load"] > 0
    assert result["stress"] > 0
    assert state.status() in {"stable", "high_stress", "overloaded"}
    state.recover(.2)
    assert state.snapshot()["energy"] >= 0


def test_internal_state_persists(tmp_path: Path, monkeypatch):
    database = Database(tmp_path / "state.db")
    monkeypatch.setattr("app.core.internal_state.db", database)
    first = InternalStateEngine()
    first.transition(uncertainty=.2, energy_delta=-.1, valence_delta=.1)
    second = InternalStateEngine()
    assert second.snapshot() == first.snapshot()
