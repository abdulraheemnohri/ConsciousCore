from __future__ import annotations
import json
import os
import sqlite3
from pathlib import Path
from typing import Any

DEFAULT_DB = Path(os.getenv("CONSCIOUSCORE_DB", "data/consciouscore.db"))

SCHEMA = """
-- Users and Sessions
CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, email TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE TABLE IF NOT EXISTS sessions (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, session_token TEXT UNIQUE NOT NULL, created_at TEXT NOT NULL DEFAULT (datetime('now')), expires_at TEXT, FOREIGN KEY (user_id) REFERENCES users(id));

-- Events
CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT NOT NULL, payload TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL DEFAULT (datetime('now')));

-- Memories (General)
CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, content TEXT NOT NULL, importance REAL NOT NULL DEFAULT 0.5, confidence REAL NOT NULL DEFAULT 0.7, tags TEXT NOT NULL DEFAULT '[]', source TEXT NOT NULL DEFAULT 'system', metadata TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL, last_accessed TEXT, access_count INTEGER NOT NULL DEFAULT 0, consolidated INTEGER NOT NULL DEFAULT 0);
CREATE INDEX IF NOT EXISTS idx_memories_kind ON memories(kind);
CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at);

-- Working Memory
CREATE TABLE IF NOT EXISTS working_memories (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT NOT NULL, importance REAL NOT NULL DEFAULT 0.5, confidence REAL NOT NULL DEFAULT 0.7, tags TEXT NOT NULL DEFAULT '[]', source TEXT NOT NULL DEFAULT 'system', metadata TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL, expires_at TEXT, pinned INTEGER NOT NULL DEFAULT 0);

-- Episodic Memory
CREATE TABLE IF NOT EXISTS episodic_memories (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT NOT NULL, importance REAL NOT NULL DEFAULT 0.5, confidence REAL NOT NULL DEFAULT 0.7, tags TEXT NOT NULL DEFAULT '[]', source TEXT NOT NULL DEFAULT 'system', metadata TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL, event_id INTEGER, FOREIGN KEY (event_id) REFERENCES events(id));

-- Semantic Memory
CREATE TABLE IF NOT EXISTS semantic_memories (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT NOT NULL, importance REAL NOT NULL DEFAULT 0.5, confidence REAL NOT NULL DEFAULT 0.7, tags TEXT NOT NULL DEFAULT '[]', source TEXT NOT NULL DEFAULT 'system', metadata TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL);

-- Procedural Memory
CREATE TABLE IF NOT EXISTS procedural_memories (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT NOT NULL, importance REAL NOT NULL DEFAULT 0.5, confidence REAL NOT NULL DEFAULT 0.7, tags TEXT NOT NULL DEFAULT '[]', source TEXT NOT NULL DEFAULT 'system', metadata TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL);

-- Self Memory
CREATE TABLE IF NOT EXISTS self_memories (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT NOT NULL, importance REAL NOT NULL DEFAULT 0.5, confidence REAL NOT NULL DEFAULT 0.7, tags TEXT NOT NULL DEFAULT '[]', source TEXT NOT NULL DEFAULT 'system', metadata TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL);

-- Meta Memory
CREATE TABLE IF NOT EXISTS meta_memories (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT NOT NULL, importance REAL NOT NULL DEFAULT 0.5, confidence REAL NOT NULL DEFAULT 0.7, tags TEXT NOT NULL DEFAULT '[]', source TEXT NOT NULL DEFAULT 'system', metadata TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL, reliability REAL NOT NULL DEFAULT 0.7);

-- Autobiographical Memory
CREATE TABLE IF NOT EXISTS autobiographical_memories (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, summary TEXT NOT NULL, content TEXT NOT NULL, importance REAL NOT NULL DEFAULT 0.5, confidence REAL NOT NULL DEFAULT 0.7, tags TEXT NOT NULL DEFAULT '[]', source TEXT NOT NULL DEFAULT 'system', metadata TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL, cycle_id INTEGER, goal_id INTEGER, plan_id INTEGER);

-- Embeddings
CREATE TABLE IF NOT EXISTS embeddings (id INTEGER PRIMARY KEY AUTOINCREMENT, memory_id INTEGER NOT NULL, embedding_vector TEXT NOT NULL, model TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT (datetime('now')), FOREIGN KEY (memory_id) REFERENCES memories(id));

-- Memory Replicas
CREATE TABLE IF NOT EXISTS memory_replicas (id INTEGER PRIMARY KEY AUTOINCREMENT, memory_id INTEGER NOT NULL, node_id TEXT NOT NULL, version INTEGER NOT NULL, checksum TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT (datetime('now')), updated_at TEXT NOT NULL DEFAULT (datetime('now')), FOREIGN KEY (memory_id) REFERENCES memories(id));

-- Memory Sync Queue
CREATE TABLE IF NOT EXISTS memory_sync_queue (id INTEGER PRIMARY KEY AUTOINCREMENT, memory_id INTEGER NOT NULL, node_id TEXT NOT NULL, action TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending', retry_count INTEGER NOT NULL DEFAULT 0, last_error TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')), updated_at TEXT NOT NULL DEFAULT (datetime('now')), FOREIGN KEY (memory_id) REFERENCES memories(id));

-- Memory Conflicts
CREATE TABLE IF NOT EXISTS memory_conflicts (id INTEGER PRIMARY KEY AUTOINCREMENT, memory_id INTEGER NOT NULL, node_id TEXT NOT NULL, conflict_type TEXT NOT NULL, resolution_status TEXT NOT NULL DEFAULT 'unresolved', resolved_by TEXT, resolved_at TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')), FOREIGN KEY (memory_id) REFERENCES memories(id));

-- Self State
CREATE TABLE IF NOT EXISTS self_state (id INTEGER PRIMARY KEY AUTOINCREMENT, energy REAL NOT NULL DEFAULT 0.5, uncertainty REAL NOT NULL DEFAULT 0.5, confidence REAL NOT NULL DEFAULT 0.5, workload REAL NOT NULL DEFAULT 0.0, attention_load REAL NOT NULL DEFAULT 0.0, task_pressure REAL NOT NULL DEFAULT 0.0, created_at TEXT NOT NULL DEFAULT (datetime('now')));

-- Capabilities
CREATE TABLE IF NOT EXISTS capabilities (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, description TEXT NOT NULL, enabled INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL DEFAULT (datetime('now')));

-- Limitations
CREATE TABLE IF NOT EXISTS limitations (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, description TEXT NOT NULL, severity TEXT NOT NULL DEFAULT 'low', created_at TEXT NOT NULL DEFAULT (datetime('now')));

-- World Entities
CREATE TABLE IF NOT EXISTS world_entities (id TEXT PRIMARY KEY, label TEXT NOT NULL, kind TEXT NOT NULL DEFAULT 'concept', created_at TEXT NOT NULL);

-- World Relations
CREATE TABLE IF NOT EXISTS world_relations (id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT NOT NULL, relation TEXT NOT NULL, target TEXT NOT NULL, confidence REAL NOT NULL DEFAULT 0.5, created_at TEXT NOT NULL);

-- World Entities V2
CREATE TABLE IF NOT EXISTS world_entities_v2 (id TEXT PRIMARY KEY, label TEXT NOT NULL, kind TEXT NOT NULL DEFAULT 'concept', properties TEXT NOT NULL DEFAULT '{}', confidence REAL NOT NULL DEFAULT 0.5, active INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_world_entities_v2_kind ON world_entities_v2(kind);

-- World Relations V2
CREATE TABLE IF NOT EXISTS world_relations_v2 (id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT NOT NULL, relation TEXT NOT NULL, target TEXT NOT NULL, confidence REAL NOT NULL DEFAULT 0.5, valid_from TEXT NOT NULL, valid_to TEXT, properties TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_world_rel_v2_source ON world_relations_v2(source);
CREATE INDEX IF NOT EXISTS idx_world_rel_v2_target ON world_relations_v2(target);

-- World Events V2
CREATE TABLE IF NOT EXISTS world_events_v2 (id INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT NOT NULL, entity_ids TEXT NOT NULL DEFAULT '[]', payload TEXT NOT NULL DEFAULT '{}', timestamp TEXT NOT NULL, source TEXT NOT NULL DEFAULT 'system');
CREATE INDEX IF NOT EXISTS idx_world_events_v2_time ON world_events_v2(timestamp);

-- World Beliefs V2
CREATE TABLE IF NOT EXISTS world_beliefs_v2 (id INTEGER PRIMARY KEY AUTOINCREMENT, statement TEXT NOT NULL, confidence REAL NOT NULL DEFAULT 0.5, evidence_refs TEXT NOT NULL DEFAULT '[]', status TEXT NOT NULL DEFAULT 'uncertain', created_at TEXT NOT NULL, updated_at TEXT NOT NULL);

-- World Entity History V2
CREATE TABLE IF NOT EXISTS world_entity_history_v2 (id INTEGER PRIMARY KEY AUTOINCREMENT, entity_id TEXT NOT NULL, action TEXT NOT NULL, state TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_world_history_v2_entity ON world_entity_history_v2(entity_id);

-- Goals
CREATE TABLE IF NOT EXISTS goals (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, priority REAL NOT NULL DEFAULT 0.5, status TEXT NOT NULL DEFAULT 'active', progress REAL NOT NULL DEFAULT 0.0, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, deadline TEXT, description TEXT);

-- Tasks
CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, goal_id INTEGER NOT NULL, title TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending', priority REAL NOT NULL DEFAULT 0.5, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, deadline TEXT, description TEXT, FOREIGN KEY (goal_id) REFERENCES goals(id));

-- Plans
CREATE TABLE IF NOT EXISTS plans (id INTEGER PRIMARY KEY AUTOINCREMENT, goal TEXT, goal_id INTEGER, constraints TEXT NOT NULL DEFAULT '[]', steps TEXT NOT NULL DEFAULT '[]', created_at TEXT NOT NULL, updated_at TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'active', progress REAL NOT NULL DEFAULT 0.0, metadata TEXT NOT NULL DEFAULT '{}', FOREIGN KEY (goal_id) REFERENCES goals(id));

-- Plan Versions
CREATE TABLE IF NOT EXISTS plan_versions (id INTEGER PRIMARY KEY AUTOINCREMENT, plan_id INTEGER NOT NULL, version INTEGER NOT NULL, steps TEXT NOT NULL DEFAULT '[]', created_at TEXT NOT NULL, FOREIGN KEY (plan_id) REFERENCES plans(id));

-- Actions
CREATE TABLE IF NOT EXISTS actions (id INTEGER PRIMARY KEY AUTOINCREMENT, task_id INTEGER NOT NULL, description TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending', created_at TEXT NOT NULL, updated_at TEXT NOT NULL, result TEXT, FOREIGN KEY (task_id) REFERENCES tasks(id));

-- Observations
CREATE TABLE IF NOT EXISTS observations (id INTEGER PRIMARY KEY AUTOINCREMENT, action_id INTEGER NOT NULL, content TEXT NOT NULL, confidence REAL NOT NULL DEFAULT 0.5, created_at TEXT NOT NULL, FOREIGN KEY (action_id) REFERENCES actions(id));

-- Reflections
CREATE TABLE IF NOT EXISTS reflections (id INTEGER PRIMARY KEY AUTOINCREMENT, summary TEXT NOT NULL, lessons TEXT NOT NULL DEFAULT '[]', uncertainties TEXT NOT NULL DEFAULT '[]', next_actions TEXT NOT NULL DEFAULT '[]', created_at TEXT NOT NULL);

-- Lessons
CREATE TABLE IF NOT EXISTS lessons (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT NOT NULL, reflection_id INTEGER NOT NULL, confidence REAL NOT NULL DEFAULT 0.5, importance REAL NOT NULL DEFAULT 0.5, created_at TEXT NOT NULL, FOREIGN KEY (reflection_id) REFERENCES reflections(id));

-- Predictions
CREATE TABLE IF NOT EXISTS predictions (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT NOT NULL, probability REAL NOT NULL DEFAULT 0.5, confidence REAL NOT NULL DEFAULT 0.5, expected_outcome TEXT, actual_outcome TEXT, error REAL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);

-- Skills
CREATE TABLE IF NOT EXISTS skills (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, description TEXT NOT NULL, enabled INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL DEFAULT (datetime('now')));

-- Skill Versions
CREATE TABLE IF NOT EXISTS skill_versions (id INTEGER PRIMARY KEY AUTOINCREMENT, skill_id INTEGER NOT NULL, version INTEGER NOT NULL, description TEXT NOT NULL, created_at TEXT NOT NULL, FOREIGN KEY (skill_id) REFERENCES skills(id));

-- Model Registry
CREATE TABLE IF NOT EXISTS model_registry (id INTEGER PRIMARY KEY AUTOINCREMENT, model_id TEXT NOT NULL UNIQUE, name TEXT NOT NULL, provider TEXT, backend TEXT, version TEXT, context_length INTEGER, capabilities TEXT NOT NULL DEFAULT '[]', quantization TEXT, size TEXT, status TEXT NOT NULL DEFAULT 'inactive', path TEXT, endpoint TEXT, health TEXT NOT NULL DEFAULT 'unknown', latency INTEGER, created_at TEXT NOT NULL DEFAULT (datetime('now')));

-- Model Runs
CREATE TABLE IF NOT EXISTS model_runs (id INTEGER PRIMARY KEY AUTOINCREMENT, model_id TEXT NOT NULL, request_id TEXT NOT NULL, prompt TEXT NOT NULL, response TEXT, latency_ms INTEGER, tokens_used INTEGER, created_at TEXT NOT NULL DEFAULT (datetime('now')), FOREIGN KEY (model_id) REFERENCES model_registry(model_id));

-- Provider Registry
CREATE TABLE IF NOT EXISTS provider_registry (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, base_url TEXT, protocol TEXT NOT NULL, model TEXT, timeout INTEGER NOT NULL DEFAULT 30, tls INTEGER NOT NULL DEFAULT 1, auth_reference TEXT, priority INTEGER NOT NULL DEFAULT 0, enabled INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL DEFAULT (datetime('now')));

-- Provider Health
CREATE TABLE IF NOT EXISTS provider_health (id INTEGER PRIMARY KEY AUTOINCREMENT, provider_id INTEGER NOT NULL, status TEXT NOT NULL DEFAULT 'unknown', latency INTEGER, last_checked TEXT NOT NULL, failure_count INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL DEFAULT (datetime('now')), FOREIGN KEY (provider_id) REFERENCES provider_registry(id));

-- Tool Registry
CREATE TABLE IF NOT EXISTS tool_registry (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, description TEXT NOT NULL, capabilities TEXT NOT NULL DEFAULT '[]', risk_level TEXT NOT NULL DEFAULT 'low', permissions TEXT NOT NULL DEFAULT '[]', input_schema TEXT NOT NULL DEFAULT '{}', output_schema TEXT NOT NULL DEFAULT '{}', enabled INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL DEFAULT (datetime('now')));

-- Permissions
CREATE TABLE IF NOT EXISTS permissions (id INTEGER PRIMARY KEY AUTOINCREMENT, tool_id INTEGER NOT NULL, action TEXT NOT NULL, allowed INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL DEFAULT (datetime('now')), FOREIGN KEY (tool_id) REFERENCES tool_registry(id));

-- Settings
CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);

-- Runtime Requests
CREATE TABLE IF NOT EXISTS runtime_requests (id INTEGER PRIMARY KEY AUTOINCREMENT, request_id TEXT NOT NULL UNIQUE, cycle_id INTEGER, mode TEXT NOT NULL, privacy TEXT NOT NULL DEFAULT 'private', task_type TEXT NOT NULL, require_local_memory INTEGER NOT NULL DEFAULT 1, allow_cloud INTEGER NOT NULL DEFAULT 0, allow_remote INTEGER NOT NULL DEFAULT 0, metadata TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL DEFAULT (datetime('now')));

-- Runtime Results
CREATE TABLE IF NOT EXISTS runtime_results (id INTEGER PRIMARY KEY AUTOINCREMENT, request_id TEXT NOT NULL, mode TEXT NOT NULL, provider TEXT, model TEXT, response TEXT, confidence REAL NOT NULL DEFAULT 0.5, degraded INTEGER NOT NULL DEFAULT 0, latency_ms INTEGER, candidates TEXT NOT NULL DEFAULT '[]', created_at TEXT NOT NULL DEFAULT (datetime('now')), FOREIGN KEY (request_id) REFERENCES runtime_requests(request_id));

-- Telemetry Events
CREATE TABLE IF NOT EXISTS telemetry_events (id INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT NOT NULL, payload TEXT NOT NULL DEFAULT '{}', metadata TEXT NOT NULL DEFAULT '{}', timestamp TEXT NOT NULL DEFAULT (datetime('now')), created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS idx_telemetry_events_type ON telemetry_events(event_type);
CREATE INDEX IF NOT EXISTS idx_telemetry_events_timestamp ON telemetry_events(timestamp);

-- Telemetry Metrics
CREATE TABLE IF NOT EXISTS telemetry_metrics (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, value REAL NOT NULL, tags TEXT NOT NULL DEFAULT '{}', timestamp TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS idx_telemetry_metrics_name ON telemetry_metrics(name);

-- Nodes
CREATE TABLE IF NOT EXISTS nodes (id INTEGER PRIMARY KEY AUTOINCREMENT, node_id TEXT NOT NULL UNIQUE, name TEXT NOT NULL, address TEXT, capabilities TEXT NOT NULL DEFAULT '[]', models TEXT NOT NULL DEFAULT '[]', memory_capacity INTEGER, cpu TEXT, ram INTEGER, gpu TEXT, status TEXT NOT NULL DEFAULT 'offline', latency INTEGER, last_seen TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')));

-- Node Health
CREATE TABLE IF NOT EXISTS node_health (id INTEGER PRIMARY KEY AUTOINCREMENT, node_id TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'unknown', cpu_usage REAL, ram_usage REAL, gpu_usage REAL, latency INTEGER, last_checked TEXT NOT NULL, failure_count INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL DEFAULT (datetime('now')), FOREIGN KEY (node_id) REFERENCES nodes(node_id));

-- Audit Logs
CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT NOT NULL, payload TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL DEFAULT (datetime('now')));

-- System Logs
CREATE TABLE IF NOT EXISTS system_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, level TEXT NOT NULL, message TEXT NOT NULL, component TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')));
"""

class Database:
    def __init__(self, path: str | Path = DEFAULT_DB):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.init()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def init(self) -> None:
        with self.connect() as conn:
            conn.executescript(SCHEMA)

    def execute(self, sql: str, params: tuple[Any, ...] = ()) -> sqlite3.Cursor:
        with self.connect() as conn:
            cur = conn.execute(sql, params)
            conn.commit()
            return cur

    def fetchall(self, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        with self.connect() as conn:
            return [dict(r) for r in conn.execute(sql, params).fetchall()]

    def fetchone(self, sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute(sql, params).fetchone()
            return dict(row) if row else None


def decode_memory(row: dict[str, Any]) -> dict[str, Any]:
    row = dict(row)
    row["tags"] = json.loads(row.get("tags") or "[]")
    row["metadata"] = json.loads(row.get("metadata") or "{}")
    row["consolidated"] = bool(row.get("consolidated", 0))
    return row


db = Database()
