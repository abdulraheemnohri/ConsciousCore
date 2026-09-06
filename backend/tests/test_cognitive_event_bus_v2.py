import pytest

from app.core.cognitive_event_bus_v2 import CognitiveEventBusV2
from app.database import db


def setup_function():
    db.execute("DROP TABLE IF EXISTS cognitive_events_v2")


def test_record_persists_and_filters():
    bus = CognitiveEventBusV2()
    first = bus.record("memory.retrieved", phase="memory", source="retriever", cycle_id="c1", payload={"count": 2}, importance=.8)
    bus.record("planning.created", phase="planning", source="planner", cycle_id="c1")
    bus.record("memory.created", phase="memory", source="memory", cycle_id="c2")
    assert first["id"]
    assert len(bus.query(phase="memory")) == 2
    assert len(bus.by_cycle("c1")) == 2
    assert bus.stats()["total"] == 3


def test_parent_and_correlation_ids():
    bus = CognitiveEventBusV2()
    parent = bus.record("planning.created", phase="planning")
    child = bus.record("safety.checked", phase="safety", correlation_id="corr-1", parent_event_id=parent["id"])
    got = bus.latest(1)[0]
    assert got["id"] == child["id"]
    assert got["correlation_id"] == "corr-1"
    assert got["parent_event_id"] == parent["id"]


@pytest.mark.asyncio
async def test_publish_records_and_delivers_live_event():
    bus = CognitiveEventBusV2()
    q = bus.subscribe()
    from app.core.events import Event
    await bus.publish(Event("loop.perception", {"_cognitive": {"cycle_id": "live-1", "phase": "perception"}, "text": "hello"}))
    assert (await q.get()).type == "loop.perception"
    assert bus.by_cycle("live-1")[0]["event_type"] == "loop.perception"
