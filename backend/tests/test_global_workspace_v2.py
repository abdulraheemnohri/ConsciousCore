from app.core.global_workspace_v2 import GlobalWorkspaceV2
from app.database import Database
import app.core.global_workspace_v2 as mod


def test_candidate_clamping_and_ranking(tmp_path, monkeypatch):
    test_db = Database(tmp_path / "workspace.db")
    monkeypatch.setattr(mod, "db", test_db)
    ws = GlobalWorkspaceV2()
    low = ws.submit_candidate("memory", "low", salience=-1, confidence=.2, urgency=.1, novelty=.1, relevance=.1)
    high = ws.submit_candidate("attention", "high", salience=1, confidence=1, urgency=1, novelty=1, relevance=1)
    assert low["salience"] == 0
    assert high["score"] > low["score"]
    assert ws.select_winner()["id"] == high["id"]


def test_broadcast_and_subscription(tmp_path, monkeypatch):
    test_db = Database(tmp_path / "workspace.db")
    monkeypatch.setattr(mod, "db", test_db)
    ws = GlobalWorkspaceV2()
    ws.subscribe("reasoning")
    candidate = ws.submit_candidate("planner", "broadcast me", urgency=.9)
    ws.select_winner()
    result = ws.broadcast(candidate["id"], approved=True)
    assert result["candidate"]["id"] == candidate["id"]
    assert "reasoning" in result["subscribers"]
    assert len(ws.history()) == 1


def test_interrupt_marks_workspace(tmp_path, monkeypatch):
    test_db = Database(tmp_path / "workspace.db")
    monkeypatch.setattr(mod, "db", test_db)
    ws = GlobalWorkspaceV2()
    ws.submit_candidate("perception", "urgent", urgency=1)
    result = ws.interrupt("urgent input")
    assert result["interrupted"] is True
    assert ws.snapshot()["interrupted"] is True
