from app.core.learning_v2 import LearningEngineV2


def test_learning_persists_and_recommends(tmp_path, monkeypatch):
    from app import database
    database.db.path = tmp_path / "learning.db"
    database.db.init()
    engine = LearningEngineV2()
    item = engine.learn("verify uncertain claims before answering", "retrieve_then_verify", ["reflection-1"], .9, .8)
    assert item["applied"] is False
    assert engine.apply(item["id"])["applied"] is True
    rec = engine.recommend(["guess_first", "retrieve_then_verify"])
    assert rec["strategy"] == "retrieve_then_verify"


def test_learning_is_bounded():
    engine = LearningEngineV2()
    item = engine.learn("bounded lesson", "safe_strategy", confidence=9, impact=-2)
    assert 0 <= item["confidence"] <= 1
    assert 0 <= item["impact"] <= 1
    assert engine.snapshot()["bounded"] is True
