import pytest
from app.core.engine import CognitiveEngine
from app.database import db

@pytest.fixture(autouse=True)
def clean_db():
    for table in ("memories", "goals", "plans", "world_entities", "world_relations", "reflections", "audit_logs"):
        db.execute(f"DELETE FROM {table}")

@pytest.mark.asyncio
async def test_pipeline_creates_memory():
    e = CognitiveEngine()
    result = await e.process("hello conscious core")
    assert "response" in result
    assert e.memory.count() == 1
    assert result["reflection"]["summary"]

@pytest.mark.asyncio
async def test_memory_retrieval():
    e = CognitiveEngine()
    e.memory.add("Python local AI memory system", importance=.9)
    result = await e.process("local AI memory")
    assert result["memories"]


def test_goals_are_persistent():
    e1 = CognitiveEngine()
    goal = e1.goals.add("Build local cognitive runtime", .9)
    e2 = CognitiveEngine()
    assert any(g["id"] == goal.id for g in e2.goals.snapshot())
    updated = e2.goals.update(goal.id, progress=1.0)
    assert updated.status == "completed"


def test_world_model_is_persistent():
    e = CognitiveEngine()
    e.world.add_entity("core", "ConsciousCore", "system")
    e.world.add_entity("memory", "Memory", "module")
    e.world.relate("core", "uses", "memory", .9)
    snapshot = CognitiveEngine().world.snapshot()
    assert len(snapshot["entities"]) == 2
    assert snapshot["relations"][0]["relation"] == "uses"


def test_safety_blocks_prohibited_action():
    e = CognitiveEngine()
    result = e.safety.evaluate("credential_capture", .9)
    assert result.allowed is False
    assert result.requires_approval is False


def test_plans_are_persistent_and_steps_update():
    e1 = CognitiveEngine()
    plan = e1.planner.create("Build the local cognitive runtime", ["offline", "safe"])
    assert plan["id"]
    assert len(plan["steps"]) == 5
    e2 = CognitiveEngine()
    loaded = e2.planner.get(plan["id"])
    assert loaded["goal"] == plan["goal"]
    updated = e2.planner.update_step(plan["id"], 1, "completed")
    assert updated["steps"][0]["status"] == "completed"


def test_planner_rejects_invalid_step_status():
    e = CognitiveEngine()
    plan = e.planner.create("Test planner validation")
    with pytest.raises(ValueError):
        e.planner.update_step(plan["id"], 1, "unknown")


def test_plan_delete_is_persistent():
    e = CognitiveEngine()
    plan = e.planner.create("Delete me")
    assert e.planner.delete(plan["id"]) is True
    assert e.planner.get(plan["id"]) is None
