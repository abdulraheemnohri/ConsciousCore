from __future__ import annotations
import json
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Any
from ..database import db


class PlanStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    PAUSED = "paused"


class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PlanStep:
    """Represents a step in a plan."""
    id: int
    action: str
    status: str = StepStatus.PENDING.value
    rationale: str = ""
    depends_on: list[int] = field(default_factory=list)
    result: str | None = None
    error: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    metadata: dict = field(default_factory=dict)
    
    def json(self) -> dict:
        return asdict(self)


@dataclass
class PlanVersion:
    """Represents a version of a plan."""
    id: int
    plan_id: int
    version: int
    steps: list[dict] = field(default_factory=list)
    created_at: str = ""
    description: str = ""
    
    def json(self) -> dict:
        return asdict(self)


@dataclass
class Plan:
    """Represents a plan with steps and constraints."""
    id: int
    goal_id: int | None = None
    goal: str = ""
    constraints: list[str] = field(default_factory=list)
    steps: list[dict] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    status: str = PlanStatus.PENDING.value
    current_step_id: int | None = None
    progress: float = 0.0
    metadata: dict = field(default_factory=dict)
    
    def json(self) -> dict:
        return asdict(self)


class Planner:
    """Enhanced planner with support for dependency graphs, parallel execution, replanning, and versioning."""
    
    def __init__(self):
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database tables for plan versions."""
        db.execute("""
            CREATE TABLE IF NOT EXISTS plan_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id INTEGER NOT NULL,
                version INTEGER NOT NULL,
                steps TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                description TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (plan_id) REFERENCES plans(id)
            )
        """)
        # Add columns to plans table if they don't exist
        try:
            db.execute("ALTER TABLE plans ADD COLUMN goal_id INTEGER")
        except:
            pass
        try:
            db.execute("ALTER TABLE plans ADD COLUMN updated_at TEXT NOT NULL DEFAULT (datetime('now'))")
        except:
            pass
        try:
            db.execute("ALTER TABLE plans ADD COLUMN status TEXT NOT NULL DEFAULT 'pending'")
        except:
            pass
        try:
            db.execute("ALTER TABLE plans ADD COLUMN current_step_id INTEGER")
        except:
            pass
        try:
            db.execute("ALTER TABLE plans ADD COLUMN progress REAL NOT NULL DEFAULT 0.0")
        except:
            pass
        try:
            db.execute("ALTER TABLE plans ADD COLUMN metadata TEXT NOT NULL DEFAULT '{}'")
        except:
            pass

    def _row_to_plan(self, row: dict) -> Plan:
        """Convert a database row to a Plan object."""
        return Plan(
            id=row["id"],
            goal_id=row.get("goal_id"),
            goal=row["goal"],
            constraints=json.loads(row.get("constraints") or "[]"),
            steps=json.loads(row.get("steps") or "[]"),
            created_at=row["created_at"],
            updated_at=row.get("updated_at", row["created_at"]),
            status=row.get("status", PlanStatus.PENDING.value),
            current_step_id=row.get("current_step_id"),
            progress=row.get("progress", 0.0),
            metadata=json.loads(row.get("metadata") or "{}")
        )

    def _row_to_plan_step(self, step_data: dict) -> PlanStep:
        """Convert a step dictionary to a PlanStep object."""
        return PlanStep(
            id=step_data["id"],
            action=step_data["action"],
            status=step_data.get("status", StepStatus.PENDING.value),
            rationale=step_data.get("rationale", ""),
            depends_on=step_data.get("depends_on", []),
            result=step_data.get("result"),
            error=step_data.get("error"),
            started_at=step_data.get("started_at"),
            completed_at=step_data.get("completed_at"),
            metadata=step_data.get("metadata", {})
        )

    # ==================== Plan Creation ====================
    
    def create(
        self,
        goal: str,
        constraints: list[str] | None = None,
        goal_id: int | None = None,
        initial_steps: list[dict] | None = None
    ) -> Plan:
        """Create a new plan with steps and constraints."""
        constraints = constraints or []
        now = datetime.now(timezone.utc).isoformat()
        
        # If no initial steps provided, create default steps
        if initial_steps is None:
            initial_steps = [
                {
                    "id": 1,
                    "action": f"Clarify desired outcome for: {goal}",
                    "rationale": "define success criteria",
                    "depends_on": []
                },
                {
                    "id": 2,
                    "action": "Gather relevant memory and current workspace context",
                    "rationale": "ground the plan",
                    "depends_on": [1]
                },
                {
                    "id": 3,
                    "action": f"Execute the smallest safe action toward: {goal}",
                    "rationale": "make measurable progress",
                    "depends_on": [2]
                },
                {
                    "id": 4,
                    "action": "Observe result and evaluate against the goal",
                    "rationale": "close action-observation loop",
                    "depends_on": [3]
                },
                {
                    "id": 5,
                    "action": "Reflect and update memory with the outcome",
                    "rationale": "retain useful learning",
                    "depends_on": [4]
                }
            ]
        
        cur = db.execute(
            """INSERT INTO plans (goal, goal_id, constraints, steps, created_at, updated_at, status, progress, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                goal,
                goal_id,
                json.dumps(constraints),
                json.dumps(initial_steps),
                now,
                now,
                PlanStatus.PENDING.value,
                0.0,
                json.dumps({})
            )
        )
        return self.get(cur.lastrowid)

    def create_from_goal(self, goal_id: int) -> Plan | None:
        """Create a plan from a goal (using goal title as the plan goal)."""
        from .goals import GoalManager
        goal_manager = GoalManager()
        goal = goal_manager.get(goal_id)
        if not goal:
            return None
        return self.create(goal.title, goal_id=goal_id)

    # ==================== Plan Retrieval ====================
    
    def _get_plan_obj(self, plan_id: int) -> Plan | None:
        row = db.fetchone("SELECT * FROM plans WHERE id=?", (plan_id,))
        if not row:
            return None
        return self._row_to_plan(row)

    def get(self, plan_id: int) -> dict | None:
        """Get a plan by ID."""
        plan = self._get_plan_obj(plan_id)
        return plan.json() if plan else None

    def get_by_goal(self, goal_id: int) -> list[Plan]:
        """Get all plans for a specific goal."""
        rows = db.fetchall("SELECT * FROM plans WHERE goal_id=? ORDER BY created_at DESC", (goal_id,))
        return [self._row_to_plan(row) for row in rows]

    def list(self, limit: int = 100) -> list[Plan]:
        """List all plans."""
        rows = db.fetchall("SELECT * FROM plans ORDER BY id DESC LIMIT ?", (max(1, min(limit, 1000)),))
        return [self._row_to_plan(row) for row in rows]

    def get_active_plans(self) -> list[Plan]:
        """Get all active (non-completed, non-failed) plans."""
        rows = db.fetchall(
            "SELECT * FROM plans WHERE status NOT IN ('completed', 'failed') ORDER BY created_at DESC"
        )
        return [self._row_to_plan(row) for row in rows]

    # ==================== Plan Updates ====================
    
    def update(
        self,
        plan_id: int,
        goal: str | None = None,
        constraints: list[str] | None = None,
        steps: list[dict] | None = None,
        status: str | None = None,
        current_step_id: int | None = None,
        progress: float | None = None,
        metadata: dict | None = None
    ) -> dict | None:
        """Update a plan."""
        plan = self._get_plan_obj(plan_id)
        if not plan:
            return None
        
        if status is not None and status not in [s.value for s in PlanStatus]:
            raise ValueError(f"invalid_plan_status:{status}")
        
        updates = []
        params = []
        if goal is not None:
            updates.append("goal=?")
            params.append(goal)
        if constraints is not None:
            updates.append("constraints=?")
            params.append(json.dumps(constraints))
        if steps is not None:
            updates.append("steps=?")
            params.append(json.dumps(steps))
        if status is not None:
            updates.append("status=?")
            params.append(status)
        if current_step_id is not None:
            updates.append("current_step_id=?")
            params.append(current_step_id)
        if progress is not None:
            updates.append("progress=?")
            params.append(max(0, min(1, progress)))
        if metadata is not None:
            updates.append("metadata=?")
            params.append(json.dumps(metadata))
        
        if updates:
            updates.append("updated_at=?")
            params.append(datetime.now(timezone.utc).isoformat())
            params.append(plan_id)
            db.execute(f"UPDATE plans SET {', '.join(updates)} WHERE id=?", tuple(params))
        
        return self.get(plan_id)

    def update_step(
        self,
        plan_id: int,
        step_id: int,
        status: str | None = None,
        result: str | None = None,
        error: str | None = None
    ) -> dict | None:
        """Update the status of a specific step in a plan."""
        plan = self._get_plan_obj(plan_id)
        if not plan:
            return None
        
        if status is not None and status not in [s.value for s in StepStatus]:
            raise ValueError(f"invalid_step_status:{status}")
        
        # Find and update the step
        updated_steps = []
        step_found = False
        for step in plan.steps:
            if step["id"] == step_id:
                step_found = True
                if status is not None:
                    step["status"] = status
                if result is not None:
                    step["result"] = result
                if error is not None:
                    step["error"] = error
                if status == StepStatus.RUNNING.value:
                    step["started_at"] = datetime.now(timezone.utc).isoformat()
                if status in [StepStatus.COMPLETED.value, StepStatus.FAILED.value, StepStatus.SKIPPED.value]:
                    step["completed_at"] = datetime.now(timezone.utc).isoformat()
            updated_steps.append(step)
        
        if not step_found:
            return None
        
        # Update the plan
        now = datetime.now(timezone.utc).isoformat()
        db.execute(
            "UPDATE plans SET steps=?, updated_at=? WHERE id=?",
            (json.dumps(updated_steps), now, plan_id)
        )
        
        # Update plan progress
        completed_steps = sum(1 for s in updated_steps if s.get("status") == StepStatus.COMPLETED.value)
        total_steps = len(updated_steps)
        progress = completed_steps / total_steps if total_steps > 0 else 0.0
        
        # Update plan status based on steps
        if all(s.get("status") == StepStatus.COMPLETED.value for s in updated_steps):
            self.update(plan_id, status=PlanStatus.COMPLETED.value, progress=1.0)
        elif any(s.get("status") == StepStatus.FAILED.value for s in updated_steps):
            self.update(plan_id, status=PlanStatus.FAILED.value)
        else:
            self.update(plan_id, progress=progress)
        
        return self.get(plan_id)

    def delete(self, plan_id: int) -> bool:
        """Delete a plan."""
        return db.execute("DELETE FROM plans WHERE id=?", (plan_id,)).rowcount > 0

    # ==================== Plan Execution ====================
    
    def start(self, plan_id: int) -> Plan | None:
        """Start executing a plan."""
        plan = self.get(plan_id)
        if not plan:
            return None
        
        if plan.status != PlanStatus.PENDING.value:
            return None
        
        # Find the first pending step
        first_step = None
        for step in plan.steps:
            if step["status"] == StepStatus.PENDING.value:
                if not step.get("depends_on"):
                    first_step = step
                    break
                else:
                    # Check if all dependencies are completed
                    deps_completed = all(
                        any(
                            s["id"] == dep_id and s["status"] == StepStatus.COMPLETED.value
                            for s in plan.steps
                        )
                        for dep_id in step["depends_on"]
                    )
                    if deps_completed:
                        first_step = step
                        break
        
        if first_step:
            self.update(plan_id, status=PlanStatus.RUNNING.value, current_step_id=first_step["id"])
            self.update_step(plan_id, first_step["id"], status=StepStatus.RUNNING.value)
        
        return self.get(plan_id)

    def advance(self, plan_id: int, step_id: int, result: str | None = None, error: str | None = None) -> Plan | None:
        """Advance a plan to the next step after completing the current one."""
        plan = self.get(plan_id)
        if not plan:
            return None
        
        if plan.status != PlanStatus.RUNNING.value:
            return None
        
        # Update current step
        current_step = None
        for step in plan.steps:
            if step["id"] == step_id:
                current_step = step
                break
        
        if not current_step:
            return None
        
        # Mark current step as completed or failed
        if error:
            self.update_step(plan_id, step_id, status=StepStatus.FAILED.value, error=error)
        else:
            self.update_step(plan_id, step_id, status=StepStatus.COMPLETED.value, result=result)
        
        # Find next step to execute
        next_step = None
        for step in plan.steps:
            if step["status"] == StepStatus.PENDING.value:
                if not step.get("depends_on"):
                    next_step = step
                    break
                else:
                    # Check if all dependencies are completed
                    deps_completed = all(
                        any(
                            s["id"] == dep_id and s["status"] == StepStatus.COMPLETED.value
                            for s in plan.steps
                        )
                        for dep_id in step["depends_on"]
                    )
                    if deps_completed:
                        next_step = step
                        break
        
        if next_step:
            self.update(plan_id, current_step_id=next_step["id"])
            self.update_step(plan_id, next_step["id"], status=StepStatus.RUNNING.value)
        else:
            # All steps completed
            self.update(plan_id, status=PlanStatus.COMPLETED.value, progress=1.0)
        
        return self.get(plan_id)

    def pause(self, plan_id: int) -> Plan | None:
        """Pause a running plan."""
        plan = self.get(plan_id)
        if not plan:
            return None
        
        if plan.status == PlanStatus.RUNNING.value:
            self.update(plan_id, status=PlanStatus.PAUSED.value)
            if plan.current_step_id:
                self.update_step(plan_id, plan.current_step_id, status=StepStatus.PAUSED.value)
        
        return self.get(plan_id)

    def resume(self, plan_id: int) -> Plan | None:
        """Resume a paused plan."""
        plan = self.get(plan_id)
        if not plan:
            return None
        
        if plan.status == PlanStatus.PAUSED.value:
            self.update(plan_id, status=PlanStatus.RUNNING.value)
            if plan.current_step_id:
                self.update_step(plan_id, plan.current_step_id, status=StepStatus.RUNNING.value)
        
        return self.get(plan_id)

    def cancel(self, plan_id: int) -> Plan | None:
        """Cancel a plan."""
        plan = self.get(plan_id)
        if not plan:
            return None
        
        self.update(plan_id, status=PlanStatus.FAILED.value)
        for step in plan.steps:
            if step["status"] in [StepStatus.PENDING.value, StepStatus.RUNNING.value]:
                self.update_step(plan_id, step["id"], status=StepStatus.SKIPPED.value)
        
        return self.get(plan_id)

    # ==================== Parallel Execution ====================
    
    def execute_parallel(self, plan_id: int) -> list[Plan]:
        """Execute all possible steps in parallel."""
        plan = self.get(plan_id)
        if not plan:
            return []
        
        if plan.status != PlanStatus.RUNNING.value:
            self.update(plan_id, status=PlanStatus.RUNNING.value)
        
        # Find all steps that can be executed in parallel
        executable_steps = []
        for step in plan.steps:
            if step["status"] == StepStatus.PENDING.value:
                if not step.get("depends_on"):
                    executable_steps.append(step)
                else:
                    # Check if all dependencies are completed
                    deps_completed = all(
                        any(
                            s["id"] == dep_id and s["status"] == StepStatus.COMPLETED.value
                            for s in plan.steps
                        )
                        for dep_id in step["depends_on"]
                    )
                    if deps_completed:
                        executable_steps.append(step)
        
        # Mark all executable steps as running
        for step in executable_steps:
            self.update_step(plan_id, step["id"], status=StepStatus.RUNNING.value)
        
        return [self.get(plan_id)]

    def complete_parallel_step(self, plan_id: int, step_id: int, result: str | None = None, error: str | None = None) -> Plan | None:
        """Complete a step that was running in parallel."""
        plan = self.get(plan_id)
        if not plan:
            return None
        
        # Update the step
        if error:
            self.update_step(plan_id, step_id, status=StepStatus.FAILED.value, error=error)
        else:
            self.update_step(plan_id, step_id, status=StepStatus.COMPLETED.value, result=result)
        
        # Check if we can execute more steps
        self.execute_parallel(plan_id)
        
        # Update plan status
        if all(s["status"] == StepStatus.COMPLETED.value for s in plan.steps):
            self.update(plan_id, status=PlanStatus.COMPLETED.value, progress=1.0)
        elif any(s["status"] == StepStatus.FAILED.value for s in plan.steps):
            self.update(plan_id, status=PlanStatus.FAILED.value)
        else:
            completed_steps = sum(1 for s in plan.steps if s["status"] == StepStatus.COMPLETED.value)
            total_steps = len(plan.steps)
            progress = completed_steps / total_steps if total_steps > 0 else 0.0
            self.update(plan_id, progress=progress)
        
        return self.get(plan_id)

    # ==================== Replanning ====================
    
    def replan(
        self,
        plan_id: int,
        new_goal: str | None = None,
        new_constraints: list[str] | None = None,
        new_steps: list[dict] | None = None
    ) -> Plan | None:
        """Create a new version of a plan with updated goal, constraints, or steps."""
        plan = self.get(plan_id)
        if not plan:
            return None
        
        # Create a new version
        version = self._get_next_version(plan_id)
        now = datetime.now(timezone.utc).isoformat()
        
        # Use existing values if not provided
        goal = new_goal or plan.goal
        constraints = new_constraints or plan.constraints
        steps = new_steps or plan.steps
        
        # Save the current plan as a version
        db.execute(
            """INSERT INTO plan_versions (plan_id, version, steps, created_at, description)
               VALUES (?, ?, ?, ?, ?)""",
            (plan_id, version - 1, json.dumps(plan.steps), now, f"Version {version - 1}")
        )
        
        # Update the plan
        self.update(
            plan_id,
            goal=goal,
            constraints=constraints,
            steps=steps,
            status=PlanStatus.PENDING.value,
            progress=0.0
        )
        
        # Save the new version
        db.execute(
            """INSERT INTO plan_versions (plan_id, version, steps, created_at, description)
               VALUES (?, ?, ?, ?, ?)""",
            (plan_id, version, json.dumps(steps), now, f"Version {version}")
        )
        
        return self.get(plan_id)

    def _get_next_version(self, plan_id: int) -> int:
        """Get the next version number for a plan."""
        versions = db.fetchall(
            "SELECT version FROM plan_versions WHERE plan_id=? ORDER BY version DESC",
            (plan_id,)
        )
        if not versions:
            return 1
        return versions[0]["version"] + 1

    def get_versions(self, plan_id: int) -> list[PlanVersion]:
        """Get all versions of a plan."""
        rows = db.fetchall(
            "SELECT * FROM plan_versions WHERE plan_id=? ORDER BY version DESC",
            (plan_id,)
        )
        return [
            PlanVersion(
                id=row["id"],
                plan_id=row["plan_id"],
                version=row["version"],
                steps=json.loads(row["steps"]),
                created_at=row["created_at"],
                description=row["description"]
            )
            for row in rows
        ]

    def rollback(self, plan_id: int, version: int) -> Plan | None:
        """Rollback a plan to a previous version."""
        plan = self.get(plan_id)
        if not plan:
            return None
        
        version_data = db.fetchone(
            "SELECT * FROM plan_versions WHERE plan_id=? AND version=?",
            (plan_id, version)
        )
        if not version_data:
            return None
        
        steps = json.loads(version_data["steps"])
        self.update(
            plan_id,
            steps=steps,
            status=PlanStatus.PENDING.value,
            progress=0.0
        )
        
        return self.get(plan_id)

    # ==================== Dependency Graph ====================
    
    def get_dependency_graph(self, plan_id: int) -> dict:
        """Get a dependency graph for a plan's steps."""
        plan = self.get(plan_id)
        if not plan:
            return {"nodes": [], "edges": []}
        
        nodes = []
        edges = []
        
        for step in plan.steps:
            nodes.append({
                "id": step["id"],
                "action": step["action"],
                "status": step.get("status", StepStatus.PENDING.value),
                "rationale": step.get("rationale", "")
            })
            for dep_id in step.get("depends_on", []):
                edges.append({"source": dep_id, "target": step["id"]})
        
        return {"nodes": nodes, "edges": edges}

    def validate_dependencies(self, plan_id: int) -> dict:
        """Validate that all dependencies in a plan are resolvable."""
        plan = self.get(plan_id)
        if not plan:
            return {"valid": False, "errors": ["Plan not found"]}
        
        errors = []
        step_ids = {step["id"] for step in plan.steps}
        
        for step in plan.steps:
            for dep_id in step.get("depends_on", []):
                if dep_id not in step_ids:
                    errors.append(f"Step {step['id']} depends on non-existent step {dep_id}")
        
        if errors:
            return {"valid": False, "errors": errors}
        
        # Check for circular dependencies
        if self._has_circular_dependencies(plan.steps):
            errors.append("Circular dependency detected")
            return {"valid": False, "errors": errors}
        
        return {"valid": True, "errors": []}

    def _has_circular_dependencies(self, steps: list[dict]) -> bool:
        """Check if a plan has circular dependencies."""
        # Build adjacency list
        graph = {step["id"]: step.get("depends_on", []) for step in steps}
        
        # Check for cycles using DFS
        visited = set()
        recursion_stack = set()
        
        def has_cycle(node):
            if node in recursion_stack:
                return True
            if node in visited:
                return False
            
            visited.add(node)
            recursion_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if has_cycle(neighbor):
                    return True
            
            recursion_stack.remove(node)
            return False
        
        for node in graph:
            if has_cycle(node):
                return True
        
        return False

    # ==================== Blocked Task Recovery ====================
    
    def recover_blocked_tasks(self, plan_id: int, strategy: str = "retry") -> Plan | None:
        """Recover blocked tasks in a plan using a specified strategy.
        
        Strategies:
        - "retry": Retry failed steps
        - "skip": Skip failed steps
        - "replan": Create a new plan version without failed steps
        """
        plan = self.get(plan_id)
        if not plan:
            return None
        
        if strategy == "retry":
            for step in plan.steps:
                if step["status"] == StepStatus.FAILED.value:
                    self.update_step(plan_id, step["id"], status=StepStatus.PENDING.value)
            self.update(plan_id, status=PlanStatus.PENDING.value)
        
        elif strategy == "skip":
            for step in plan.steps:
                if step["status"] == StepStatus.FAILED.value:
                    self.update_step(plan_id, step["id"], status=StepStatus.SKIPPED.value)
            
            # Check if we can proceed
            self.execute_parallel(plan_id)
        
        elif strategy == "replan":
            # Create a new version without failed steps
            new_steps = [step for step in plan.steps if step["status"] != StepStatus.FAILED.value]
            self.replan(plan_id, new_steps=new_steps)
        
        return self.get(plan_id)

    # ==================== Plan Analytics ====================
    
    def get_plan_analytics(self, plan_id: int) -> dict:
        """Get analytics for a plan (completion rate, step times, etc.)."""
        plan = self.get(plan_id)
        if not plan:
            return {}
        
        total_steps = len(plan.steps)
        completed_steps = sum(1 for s in plan.steps if s["status"] == StepStatus.COMPLETED.value)
        failed_steps = sum(1 for s in plan.steps if s["status"] == StepStatus.FAILED.value)
        pending_steps = sum(1 for s in plan.steps if s["status"] == StepStatus.PENDING.value)
        
        # Calculate step durations (if available)
        step_durations = []
        for step in plan.steps:
            if step.get("started_at") and step.get("completed_at"):
                try:
                    start = datetime.fromisoformat(step["started_at"])
                    end = datetime.fromisoformat(step["completed_at"])
                    step_durations.append((end - start).total_seconds())
                except:
                    pass
        
        avg_step_duration = sum(step_durations) / len(step_durations) if step_durations else 0
        
        return {
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "failed_steps": failed_steps,
            "pending_steps": pending_steps,
            "completion_rate": completed_steps / total_steps if total_steps > 0 else 0,
            "avg_step_duration_seconds": avg_step_duration,
            "status": plan.status,
            "progress": plan.progress
        }
