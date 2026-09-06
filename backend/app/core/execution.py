from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from .planner import Planner
from .safety import SafetyEngine
from .memory import MemoryStore

@dataclass
class ExecutionResult:
    plan_id: int
    step_id: int
    status: str
    phase: str
    observed: str
    approval_required: bool
    allowed: bool
    reason: str
    timestamp: str

class ExecutionEngine:
    """Runs planner steps as a local, observable state machine.

    This V2 executor does not perform arbitrary external side effects. It evaluates
    the requested step through the safety layer, records an observation, and moves
    the planner state forward. Real tools can be attached later behind authorization.
    """
    def __init__(self, planner: Planner, safety: SafetyEngine, memory: MemoryStore):
        self.planner = planner
        self.safety = safety
        self.memory = memory
        self.last: ExecutionResult | None = None

    def advance(self, plan_id: int, step_id: int, risk: float = .5, approved: bool = False):
        plan = self.planner.get(plan_id)
        if not plan:
            return None
        step = next((x for x in plan["steps"] if x["id"] == step_id), None)
        if not step:
            return None
        permission = self.safety.evaluate(step["action"], risk)
        now = datetime.now(timezone.utc).isoformat()
        if not permission.allowed:
            result = ExecutionResult(plan_id, step_id, "blocked", "safety", "Execution blocked by safety policy.", False, False, permission.reason, now)
        elif permission.requires_approval and not approved:
            result = ExecutionResult(plan_id, step_id, "awaiting_approval", "approval", "Execution is waiting for explicit approval.", True, True, permission.reason, now)
        else:
            updated = self.planner.update_step(plan_id, step_id, "running")
            updated = self.planner.update_step(plan_id, step_id, "completed")
            observation = f"Local execution simulation completed for step {step_id}: {step['action']}"
            self.memory.add(
                f"Plan #{plan_id} step #{step_id}: {observation}",
                kind="episodic", importance=.6, confidence=.85,
                metadata={"plan_id": plan_id, "step_id": step_id, "phase": "observation"},
                tags=["execution", "planner", "observation"], source="execution"
            )
            result = ExecutionResult(plan_id, step_id, "completed", "observation", observation, False, True, "local simulation only", now)
        self.last = result
        return {**asdict(result), "plan": self.planner.get(plan_id)}

    def snapshot(self):
        return asdict(self.last) if self.last else None
