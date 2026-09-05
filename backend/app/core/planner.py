from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

@dataclass
class PlanStep:
    id: int
    action: str
    status: str = "pending"
    rationale: str = ""

class Planner:
    def create(self, goal: str, constraints: list[str] | None = None) -> dict:
        constraints = constraints or []
        steps = [
            PlanStep(1, f"Clarify desired outcome for: {goal}", rationale="define success criteria"),
            PlanStep(2, "Gather relevant memory and current workspace context", rationale="ground the plan in available context"),
            PlanStep(3, f"Execute the smallest safe action toward: {goal}", rationale="progress while minimizing risk"),
            PlanStep(4, "Observe result and evaluate against the goal", rationale="close the action-observation loop"),
            PlanStep(5, "Reflect and update memory with the outcome", rationale="retain useful learning"),
        ]
        return {"goal": goal, "constraints": constraints, "created_at": datetime.now(timezone.utc).isoformat(), "steps": [asdict(x) for x in steps]}
