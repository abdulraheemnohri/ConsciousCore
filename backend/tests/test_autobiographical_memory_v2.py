import pytest
from app.core.autobiographical_memory_v2 import AutobiographicalMemoryV2
from app import database

@pytest.fixture
def store(tmp_path):
    old = database.db.path
    database.db.path = tmp_path / "auto.db"
    database.db.init()
    s = AutobiographicalMemoryV2()
    yield s
    database.db.path = old

def test_create_get_and_stats(store):
    e = store.create(cycle_id=7, title="Build test", summary="A useful episode", input_text="hello", response_summary="world", tags=["test"], importance=2, confidence=-1)
    assert e["cycle_id"] == 7
    assert e["importance"] == 1.0 and e["confidence"] == 0.0
    assert store.get(e["id"])["title"] == "Build test"
    assert store.stats()["total"] == 1

def test_search_timeline_archive(store):
    a = store.create(title="First", summary="alpha", started_at="2026-01-01T00:00:00+00:00")
    b = store.create(title="Second", summary="beta", started_at="2026-01-02T00:00:00+00:00")
    assert store.search("alpha")[0]["id"] == a["id"]
    assert [x["id"] for x in store.timeline()] == [a["id"], b["id"]]
    store.archive(a["id"])
    assert store.stats()["archived"] == 1
    assert all(x["id"] != a["id"] for x in store.list())
