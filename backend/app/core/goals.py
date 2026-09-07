from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Any
import json
from ..database import db


class GoalStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class GoalPriority(Enum):
    LOW = 0.25
    MEDIUM = 0.5
    HIGH = 0.75
    CRITICAL = 1.0


@dataclass
class Goal:
    """Represents a goal in the system."""
    id: int
    title: str
    description: str = ""
    priority: float = 0.5
    status: str = "active"
    progress: float = 0.0
    created_at: str = ""
    updated_at: str = ""
    deadline: str | None = None
    parent_id: int | None = None  # For hierarchical goals
    dependencies: list[int] = field(default_factory=list)  # IDs of goals this depends on
    success_criteria: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    
    def json(self) -> dict:
        return asdict(self)


@dataclass
class Task:
    """Represents a task within a goal."""
    id: int
    goal_id: int
    title: str
    description: str = ""
    status: str = "pending"
    priority: float = 0.5
    created_at: str = ""
    updated_at: str = ""
    deadline: str | None = None
    dependencies: list[int] = field(default_factory=list)  # IDs of tasks this depends on
    
    def json(self) -> dict:
        return asdict(self)


@dataclass
class Objective:
    """Represents an objective, which is a higher-level goal."""
    id: int
    title: str
    description: str = ""
    priority: float = 0.5
    status: str = "active"
    progress: float = 0.0
    created_at: str = ""
    updated_at: str = ""
    deadline: str | None = None
    parent_id: int | None = None  # For hierarchical objectives
    
    def json(self) -> dict:
        return asdict(self)


@dataclass
class Mission:
    """Represents a mission, which is the highest-level goal."""
    id: int
    title: str
    description: str = ""
    priority: float = 1.0
    status: str = "active"
    progress: float = 0.0
    created_at: str = ""
    updated_at: str = ""
    
    def json(self) -> dict:
        return asdict(self)


class GoalManager:
    """Manages goals, tasks, objectives, and missions with hierarchical support."""
    
    def __init__(self):
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database tables for tasks and objectives."""
        db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'pending',
                priority REAL NOT NULL DEFAULT 0.5,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                deadline TEXT,
                dependencies TEXT NOT NULL DEFAULT '[]',
                FOREIGN KEY (goal_id) REFERENCES goals(id)
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS objectives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                priority REAL NOT NULL DEFAULT 0.5,
                status TEXT NOT NULL DEFAULT 'active',
                progress REAL NOT NULL DEFAULT 0.0,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                deadline TEXT,
                parent_id INTEGER
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS missions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                priority REAL NOT NULL DEFAULT 1.0,
                status TEXT NOT NULL DEFAULT 'active',
                progress REAL NOT NULL DEFAULT 0.0,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        # Add columns to goals table if they don't exist
        try:
            db.execute("ALTER TABLE goals ADD COLUMN description TEXT NOT NULL DEFAULT ''")
        except:
            pass
        try:
            db.execute("ALTER TABLE goals ADD COLUMN updated_at TEXT NOT NULL DEFAULT (datetime('now'))")
        except:
            pass
        try:
            db.execute("ALTER TABLE goals ADD COLUMN deadline TEXT")
        except:
            pass
        try:
            db.execute("ALTER TABLE goals ADD COLUMN parent_id INTEGER")
        except:
            pass
        try:
            db.execute("ALTER TABLE goals ADD COLUMN dependencies TEXT NOT NULL DEFAULT '[]'")
        except:
            pass
        try:
            db.execute("ALTER TABLE goals ADD COLUMN success_criteria TEXT NOT NULL DEFAULT '[]'")
        except:
            pass
        try:
            db.execute("ALTER TABLE goals ADD COLUMN tags TEXT NOT NULL DEFAULT '[]'")
        except:
            pass
        try:
            db.execute("ALTER TABLE goals ADD COLUMN metadata TEXT NOT NULL DEFAULT '{}'")
        except:
            pass

    # ==================== Goal Operations ====================
    
    def add(
        self,
        title: str,
        description: str = "",
        priority: float = 0.5,
        deadline: str | None = None,
        parent_id: int | None = None,
        dependencies: list[int] | None = None,
        success_criteria: list[str] | None = None,
        tags: list[str] | None = None,
        metadata: dict | None = None
    ) -> Goal:
        """Add a new goal."""
        now = datetime.now(timezone.utc).isoformat()
        cur = db.execute(
            """INSERT INTO goals (title, description, priority, status, progress, created_at, updated_at, deadline, parent_id, dependencies, success_criteria, tags, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                title,
                description,
                max(0, min(1, priority)),
                GoalStatus.ACTIVE.value,
                0.0,
                now,
                now,
                deadline,
                parent_id,
                json.dumps(dependencies or []),
                json.dumps(success_criteria or []),
                json.dumps(tags or []),
                json.dumps(metadata or {})
            )
        )
        return self.get(cur.lastrowid)

    def get(self, goal_id: int) -> Goal | None:
        """Get a goal by ID."""
        row = db.fetchone("SELECT * FROM goals WHERE id=?", (goal_id,))
        if not row:
            return None
        return Goal(
            id=row["id"],
            title=row["title"],
            description=row.get("description", ""),
            priority=row["priority"],
            status=row["status"],
            progress=row["progress"],
            created_at=row["created_at"],
            updated_at=row.get("updated_at", row["created_at"]),
            deadline=row.get("deadline"),
            parent_id=row.get("parent_id"),
            dependencies=json.loads(row.get("dependencies") or "[]"),
            success_criteria=json.loads(row.get("success_criteria") or "[]"),
            tags=json.loads(row.get("tags") or "[]"),
            metadata=json.loads(row.get("metadata") or "{}")
        )

    def update(
        self,
        goal_id: int,
        title: str | None = None,
        description: str | None = None,
        progress: float | None = None,
        status: str | None = None,
        priority: float | None = None,
        deadline: str | None = None,
        parent_id: int | None = None,
        dependencies: list[int] | None = None,
        success_criteria: list[str] | None = None,
        tags: list[str] | None = None,
        metadata: dict | None = None
    ) -> Goal | None:
        """Update a goal."""
        goal = self.get(goal_id)
        if not goal:
            return None
        
        if status is not None and status not in [s.value for s in GoalStatus]:
            raise ValueError(f"invalid_goal_status:{status}")
        
        p = max(0, min(1, progress)) if progress is not None else goal.progress
        s = status if status is not None else goal.status
        if p >= 1:
            s = GoalStatus.COMPLETED.value
        
        pr = max(0, min(1, priority)) if priority is not None else goal.priority
        now = datetime.now(timezone.utc).isoformat()
        
        updates = []
        params = []
        if title is not None:
            updates.append("title=?")
            params.append(title)
        if description is not None:
            updates.append("description=?")
            params.append(description)
        if progress is not None or status is not None:
            updates.append("progress=?")
            params.append(p)
            updates.append("status=?")
            params.append(s)
        if priority is not None:
            updates.append("priority=?")
            params.append(pr)
        if deadline is not None:
            updates.append("deadline=?")
            params.append(deadline)
        if parent_id is not None:
            updates.append("parent_id=?")
            params.append(parent_id)
        if dependencies is not None:
            updates.append("dependencies=?")
            params.append(json.dumps(dependencies))
        if success_criteria is not None:
            updates.append("success_criteria=?")
            params.append(json.dumps(success_criteria))
        if tags is not None:
            updates.append("tags=?")
            params.append(json.dumps(tags))
        if metadata is not None:
            updates.append("metadata=?")
            params.append(json.dumps(metadata))
        
        if updates:
            updates.append("updated_at=?")
            params.append(now)
            params.append(goal_id)
            db.execute(f"UPDATE goals SET {', '.join(updates)} WHERE id=?", tuple(params))
        
        return self.get(goal_id)

    def delete(self, goal_id: int) -> bool:
        """Delete a goal."""
        return db.execute("DELETE FROM goals WHERE id=?", (goal_id,)).rowcount > 0

    def snapshot(self) -> list[dict]:
        """Get all goals as a list of dictionaries."""
        return [dict(row) for row in db.fetchall("SELECT * FROM goals ORDER BY priority DESC, id")]

    def active(self) -> list[dict]:
        """Get all active goals."""
        return [dict(row) for row in db.fetchall("SELECT * FROM goals WHERE status='active' ORDER BY priority DESC, id")]

    def paused(self) -> list[dict]:
        """Get all paused goals."""
        return [dict(row) for row in db.fetchall("SELECT * FROM goals WHERE status='paused' ORDER BY priority DESC, id")]

    def completed(self) -> list[dict]:
        """Get all completed goals."""
        return [dict(row) for row in db.fetchall("SELECT * FROM goals WHERE status='completed' ORDER BY priority DESC, id")]

    def failed(self) -> list[dict]:
        """Get all failed goals."""
        return [dict(row) for row in db.fetchall("SELECT * FROM goals WHERE status='failed' ORDER BY priority DESC, id")]

    def archived(self) -> list[dict]:
        """Get all archived goals."""
        return [dict(row) for row in db.fetchall("SELECT * FROM goals WHERE status='archived' ORDER BY priority DESC, id")]

    def get_by_parent(self, parent_id: int) -> list[Goal]:
        """Get all goals with a specific parent."""
        rows = db.fetchall("SELECT * FROM goals WHERE parent_id=? ORDER BY priority DESC, id", (parent_id,))
        return [
            Goal(
                id=row["id"],
                title=row["title"],
                description=row.get("description", ""),
                priority=row["priority"],
                status=row["status"],
                progress=row["progress"],
                created_at=row["created_at"],
                updated_at=row.get("updated_at", row["created_at"]),
                deadline=row.get("deadline"),
                parent_id=row.get("parent_id"),
                dependencies=json.loads(row.get("dependencies") or "[]"),
                success_criteria=json.loads(row.get("success_criteria") or "[]"),
                tags=json.loads(row.get("tags") or "[]"),
                metadata=json.loads(row.get("metadata") or "{}")
            )
            for row in rows
        ]

    def get_dependencies(self, goal_id: int) -> list[Goal]:
        """Get all dependencies for a goal."""
        goal = self.get(goal_id)
        if not goal or not goal.dependencies:
            return []
        return [self.get(dep_id) for dep_id in goal.dependencies if self.get(dep_id)]

    def pause(self, goal_id: int) -> Goal | None:
        """Pause a goal."""
        return self.update(goal_id, status=GoalStatus.PAUSED.value)

    def resume(self, goal_id: int) -> Goal | None:
        """Resume a paused goal."""
        return self.update(goal_id, status=GoalStatus.ACTIVE.value)

    def complete(self, goal_id: int) -> Goal | None:
        """Mark a goal as completed."""
        return self.update(goal_id, status=GoalStatus.COMPLETED.value, progress=1.0)

    def cancel(self, goal_id: int) -> Goal | None:
        """Cancel a goal."""
        return self.update(goal_id, status=GoalStatus.CANCELLED.value)

    def archive(self, goal_id: int) -> Goal | None:
        """Archive a goal."""
        return self.update(goal_id, status=GoalStatus.ARCHIVED.value)

    def update_progress(self, goal_id: int, progress: float) -> Goal | None:
        """Update the progress of a goal."""
        return self.update(goal_id, progress=max(0, min(1, progress)))

    # ==================== Task Operations ====================
    
    def add_task(
        self,
        goal_id: int,
        title: str,
        description: str = "",
        priority: float = 0.5,
        deadline: str | None = None,
        dependencies: list[int] | None = None
    ) -> Task:
        """Add a task to a goal."""
        now = datetime.now(timezone.utc).isoformat()
        cur = db.execute(
            """INSERT INTO tasks (goal_id, title, description, status, priority, created_at, updated_at, deadline, dependencies)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                goal_id,
                title,
                description,
                "pending",
                max(0, min(1, priority)),
                now,
                now,
                deadline,
                json.dumps(dependencies or [])
            )
        )
        return self.get_task(cur.lastrowid)

    def get_task(self, task_id: int) -> Task | None:
        """Get a task by ID."""
        row = db.fetchone("SELECT * FROM tasks WHERE id=?", (task_id,))
        if not row:
            return None
        return Task(
            id=row["id"],
            goal_id=row["goal_id"],
            title=row["title"],
            description=row.get("description", ""),
            status=row["status"],
            priority=row["priority"],
            created_at=row["created_at"],
            updated_at=row.get("updated_at", row["created_at"]),
            deadline=row.get("deadline"),
            dependencies=json.loads(row.get("dependencies") or "[]")
        )

    def update_task(
        self,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
        status: str | None = None,
        priority: float | None = None,
        deadline: str | None = None,
        dependencies: list[int] | None = None
    ) -> Task | None:
        """Update a task."""
        task = self.get_task(task_id)
        if not task:
            return None
        
        updates = []
        params = []
        if title is not None:
            updates.append("title=?")
            params.append(title)
        if description is not None:
            updates.append("description=?")
            params.append(description)
        if status is not None:
            updates.append("status=?")
            params.append(status)
        if priority is not None:
            updates.append("priority=?")
            params.append(max(0, min(1, priority)))
        if deadline is not None:
            updates.append("deadline=?")
            params.append(deadline)
        if dependencies is not None:
            updates.append("dependencies=?")
            params.append(json.dumps(dependencies))
        
        if updates:
            updates.append("updated_at=?")
            params.append(datetime.now(timezone.utc).isoformat())
            params.append(task_id)
            db.execute(f"UPDATE tasks SET {', '.join(updates)} WHERE id=?", tuple(params))
        
        return self.get_task(task_id)

    def delete_task(self, task_id: int) -> bool:
        """Delete a task."""
        return db.execute("DELETE FROM tasks WHERE id=?", (task_id,)).rowcount > 0

    def get_tasks_by_goal(self, goal_id: int) -> list[Task]:
        """Get all tasks for a goal."""
        rows = db.fetchall("SELECT * FROM tasks WHERE goal_id=? ORDER BY priority DESC, id", (goal_id,))
        return [
            Task(
                id=row["id"],
                goal_id=row["goal_id"],
                title=row["title"],
                description=row.get("description", ""),
                status=row["status"],
                priority=row["priority"],
                created_at=row["created_at"],
                updated_at=row.get("updated_at", row["created_at"]),
                deadline=row.get("deadline"),
                dependencies=json.loads(row.get("dependencies") or "[]")
            )
            for row in rows
        ]

    def get_blocked_tasks(self) -> list[Task]:
        """Get all tasks that are blocked by dependencies."""
        all_tasks = [self.get_task(row["id"]) for row in db.fetchall("SELECT * FROM tasks")]
        blocked = []
        for task in all_tasks:
            if not task:
                continue
            if task.dependencies:
                deps_completed = all(
                    self.get_task(dep_id).status == "completed"
                    for dep_id in task.dependencies
                    if self.get_task(dep_id)
                )
                if not deps_completed:
                    blocked.append(task)
        return blocked

    # ==================== Objective Operations ====================
    
    def add_objective(
        self,
        title: str,
        description: str = "",
        priority: float = 0.5,
        deadline: str | None = None,
        parent_id: int | None = None
    ) -> Objective:
        """Add a new objective."""
        now = datetime.now(timezone.utc).isoformat()
        cur = db.execute(
            """INSERT INTO objectives (title, description, priority, status, progress, created_at, updated_at, deadline, parent_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                title,
                description,
                max(0, min(1, priority)),
                "active",
                0.0,
                now,
                now,
                deadline,
                parent_id
            )
        )
        return self.get_objective(cur.lastrowid)

    def get_objective(self, objective_id: int) -> Objective | None:
        """Get an objective by ID."""
        row = db.fetchone("SELECT * FROM objectives WHERE id=?", (objective_id,))
        if not row:
            return None
        return Objective(
            id=row["id"],
            title=row["title"],
            description=row.get("description", ""),
            priority=row["priority"],
            status=row["status"],
            progress=row["progress"],
            created_at=row["created_at"],
            updated_at=row.get("updated_at", row["created_at"]),
            deadline=row.get("deadline"),
            parent_id=row.get("parent_id")
        )

    def update_objective(
        self,
        objective_id: int,
        title: str | None = None,
        description: str | None = None,
        progress: float | None = None,
        status: str | None = None,
        priority: float | None = None,
        deadline: str | None = None,
        parent_id: int | None = None
    ) -> Objective | None:
        """Update an objective."""
        objective = self.get_objective(objective_id)
        if not objective:
            return None
        
        updates = []
        params = []
        if title is not None:
            updates.append("title=?")
            params.append(title)
        if description is not None:
            updates.append("description=?")
            params.append(description)
        if progress is not None:
            updates.append("progress=?")
            params.append(max(0, min(1, progress)))
        if status is not None:
            updates.append("status=?")
            params.append(status)
        if priority is not None:
            updates.append("priority=?")
            params.append(max(0, min(1, priority)))
        if deadline is not None:
            updates.append("deadline=?")
            params.append(deadline)
        if parent_id is not None:
            updates.append("parent_id=?")
            params.append(parent_id)
        
        if updates:
            updates.append("updated_at=?")
            params.append(datetime.now(timezone.utc).isoformat())
            params.append(objective_id)
            db.execute(f"UPDATE objectives SET {', '.join(updates)} WHERE id=?", tuple(params))
        
        return self.get_objective(objective_id)

    def delete_objective(self, objective_id: int) -> bool:
        """Delete an objective."""
        return db.execute("DELETE FROM objectives WHERE id=?", (objective_id,)).rowcount > 0

    def get_objectives_by_parent(self, parent_id: int | None = None) -> list[Objective]:
        """Get all objectives with a specific parent (or root objectives if None)."""
        if parent_id is None:
            rows = db.fetchall("SELECT * FROM objectives WHERE parent_id IS NULL ORDER BY priority DESC, id")
        else:
            rows = db.fetchall("SELECT * FROM objectives WHERE parent_id=? ORDER BY priority DESC, id", (parent_id,))
        return [
            Objective(
                id=row["id"],
                title=row["title"],
                description=row.get("description", ""),
                priority=row["priority"],
                status=row["status"],
                progress=row["progress"],
                created_at=row["created_at"],
                updated_at=row.get("updated_at", row["created_at"]),
                deadline=row.get("deadline"),
                parent_id=row.get("parent_id")
            )
            for row in rows
        ]

    # ==================== Mission Operations ====================
    
    def add_mission(
        self,
        title: str,
        description: str = ""
    ) -> Mission:
        """Add a new mission."""
        now = datetime.now(timezone.utc).isoformat()
        cur = db.execute(
            """INSERT INTO missions (title, description, priority, status, progress, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (title, description, 1.0, "active", 0.0, now, now)
        )
        return self.get_mission(cur.lastrowid)

    def get_mission(self, mission_id: int) -> Mission | None:
        """Get a mission by ID."""
        row = db.fetchone("SELECT * FROM missions WHERE id=?", (mission_id,))
        if not row:
            return None
        return Mission(
            id=row["id"],
            title=row["title"],
            description=row.get("description", ""),
            priority=row["priority"],
            status=row["status"],
            progress=row["progress"],
            created_at=row["created_at"],
            updated_at=row.get("updated_at", row["created_at"])
        )

    def update_mission(
        self,
        mission_id: int,
        title: str | None = None,
        description: str | None = None,
        progress: float | None = None,
        status: str | None = None
    ) -> Mission | None:
        """Update a mission."""
        mission = self.get_mission(mission_id)
        if not mission:
            return None
        
        updates = []
        params = []
        if title is not None:
            updates.append("title=?")
            params.append(title)
        if description is not None:
            updates.append("description=?")
            params.append(description)
        if progress is not None:
            updates.append("progress=?")
            params.append(max(0, min(1, progress)))
        if status is not None:
            updates.append("status=?")
            params.append(status)
        
        if updates:
            updates.append("updated_at=?")
            params.append(datetime.now(timezone.utc).isoformat())
            params.append(mission_id)
            db.execute(f"UPDATE missions SET {', '.join(updates)} WHERE id=?", tuple(params))
        
        return self.get_mission(mission_id)

    def delete_mission(self, mission_id: int) -> bool:
        """Delete a mission."""
        return db.execute("DELETE FROM missions WHERE id=?", (mission_id,)).rowcount > 0

    def get_all_missions(self) -> list[Mission]:
        """Get all missions."""
        rows = db.fetchall("SELECT * FROM missions ORDER BY priority DESC, id")
        return [
            Mission(
                id=row["id"],
                title=row["title"],
                description=row.get("description", ""),
                priority=row["priority"],
                status=row["status"],
                progress=row["progress"],
                created_at=row["created_at"],
                updated_at=row.get("updated_at", row["created_at"])
            )
            for row in rows
        ]

    # ==================== Hierarchy Operations ====================
    
    def get_goal_hierarchy(self, goal_id: int) -> dict:
        """Get the full hierarchy for a goal (mission -> objective -> goal -> tasks)."""
        goal = self.get(goal_id)
        if not goal:
            return {}
        
        # Find the parent chain
        parent_chain = []
        current = goal
        while current and current.parent_id:
            parent = self.get(current.parent_id)
            if parent:
                parent_chain.insert(0, parent)
            current = parent
        
        # Get tasks for this goal
        tasks = self.get_tasks_by_goal(goal_id)
        
        return {
            "goal": goal.json(),
            "parent_chain": [g.json() for g in parent_chain],
            "tasks": [t.json() for t in tasks]
        }

    def get_full_hierarchy(self) -> dict:
        """Get the complete hierarchy (missions -> objectives -> goals -> tasks)."""
        missions = self.get_all_missions()
        objectives = self.get_objectives_by_parent()
        goals = [self.get(g["id"]) for g in self.snapshot()]
        
        hierarchy = {
            "missions": [m.json() for m in missions],
            "objectives": [o.json() for o in objectives],
            "goals": [g.json() for g in goals if g]
        }
        
        # Add tasks for each goal
        for goal in hierarchy["goals"]:
            tasks = self.get_tasks_by_goal(goal["id"])
            goal["tasks"] = [t.json() for t in tasks]
        
        return hierarchy

    # ==================== Dependency Graph ====================
    
    def get_dependency_graph(self, goal_id: int | None = None) -> dict:
        """Get a dependency graph for goals (or a specific goal)."""
        if goal_id:
            goal = self.get(goal_id)
            if not goal:
                return {"nodes": [], "edges": []}
            
            # Get all goals in the dependency chain
            all_goals = {goal.id: goal}
            to_process = [goal]
            while to_process:
                current = to_process.pop()
                for dep_id in current.dependencies:
                    dep = self.get(dep_id)
                    if dep and dep.id not in all_goals:
                        all_goals[dep.id] = dep
                        to_process.append(dep)
            
            # Build nodes and edges
            nodes = [
                {
                    "id": g.id,
                    "title": g.title,
                    "status": g.status,
                    "progress": g.progress
                }
                for g in all_goals.values()
            ]
            edges = []
            for g in all_goals.values():
                for dep_id in g.dependencies:
                    if dep_id in all_goals:
                        edges.append({"source": dep_id, "target": g.id})
            
            return {"nodes": nodes, "edges": edges}
        else:
            # Get dependency graph for all goals
            all_goals = [self.get(g["id"]) for g in self.snapshot()]
            all_goals = [g for g in all_goals if g]
            
            nodes = [
                {
                    "id": g.id,
                    "title": g.title,
                    "status": g.status,
                    "progress": g.progress
                }
                for g in all_goals
            ]
            edges = []
            for g in all_goals:
                for dep_id in g.dependencies:
                    edges.append({"source": dep_id, "target": g.id})
            
            return {"nodes": nodes, "edges": edges}
