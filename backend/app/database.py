from __future__ import annotations
import json
import os
import sqlite3
from pathlib import Path
from typing import Any

DEFAULT_DB = Path(os.getenv("CONSCIOUSCORE_DB", "data/consciouscore.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, content TEXT NOT NULL, importance REAL NOT NULL DEFAULT 0.5, confidence REAL NOT NULL DEFAULT 0.7, tags TEXT NOT NULL DEFAULT '[]', source TEXT NOT NULL DEFAULT 'system', metadata TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL, last_accessed TEXT, access_count INTEGER NOT NULL DEFAULT 0, consolidated INTEGER NOT NULL DEFAULT 0);
CREATE INDEX IF NOT EXISTS idx_memories_kind ON memories(kind);
CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at);
CREATE TABLE IF NOT EXISTS goals (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, priority REAL NOT NULL DEFAULT 0.5, status TEXT NOT NULL DEFAULT 'active', progress REAL NOT NULL DEFAULT 0.0, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS plans (id INTEGER PRIMARY KEY AUTOINCREMENT, goal TEXT NOT NULL, constraints TEXT NOT NULL DEFAULT '[]', steps TEXT NOT NULL DEFAULT '[]', created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS world_entities (id TEXT PRIMARY KEY, label TEXT NOT NULL, kind TEXT NOT NULL DEFAULT 'concept', created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS world_relations (id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT NOT NULL, relation TEXT NOT NULL, target TEXT NOT NULL, confidence REAL NOT NULL DEFAULT 0.5, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS world_entities_v2 (id TEXT PRIMARY KEY, label TEXT NOT NULL, kind TEXT NOT NULL DEFAULT 'concept', properties TEXT NOT NULL DEFAULT '{}', confidence REAL NOT NULL DEFAULT 0.5, active INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS world_relations_v2 (id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT NOT NULL, relation TEXT NOT NULL, target TEXT NOT NULL, confidence REAL NOT NULL DEFAULT 0.5, valid_from TEXT NOT NULL, valid_to TEXT, properties TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_world_rel_v2_source ON world_relations_v2(source);
CREATE INDEX IF NOT EXISTS idx_world_rel_v2_target ON world_relations_v2(target);
CREATE TABLE IF NOT EXISTS world_events_v2 (id INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT NOT NULL, entity_ids TEXT NOT NULL DEFAULT '[]', payload TEXT NOT NULL DEFAULT '{}', timestamp TEXT NOT NULL, source TEXT NOT NULL DEFAULT 'system');
CREATE INDEX IF NOT EXISTS idx_world_events_v2_time ON world_events_v2(timestamp);
CREATE TABLE IF NOT EXISTS world_beliefs_v2 (id INTEGER PRIMARY KEY AUTOINCREMENT, statement TEXT NOT NULL, confidence REAL NOT NULL DEFAULT 0.5, evidence_refs TEXT NOT NULL DEFAULT '[]', status TEXT NOT NULL DEFAULT 'uncertain', created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS world_entity_history_v2 (id INTEGER PRIMARY KEY AUTOINCREMENT, entity_id TEXT NOT NULL, action TEXT NOT NULL, state TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_world_history_v2_entity ON world_entity_history_v2(entity_id);
CREATE TABLE IF NOT EXISTS reflections (id INTEGER PRIMARY KEY AUTOINCREMENT, summary TEXT NOT NULL, lessons TEXT NOT NULL DEFAULT '[]', uncertainties TEXT NOT NULL DEFAULT '[]', next_actions TEXT NOT NULL DEFAULT '[]', created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT NOT NULL, payload TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
"""

class Database:
    def __init__(self, path: str | Path = DEFAULT_DB):
        self.path = Path(path); self.path.parent.mkdir(parents=True, exist_ok=True); self.init()
    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path); conn.row_factory = sqlite3.Row; return conn
    def init(self) -> None:
        with self.connect() as conn: conn.executescript(SCHEMA)
    def execute(self, sql: str, params: tuple[Any, ...] = ()) -> sqlite3.Cursor:
        with self.connect() as conn: cur = conn.execute(sql, params); conn.commit(); return cur
    def fetchall(self, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        with self.connect() as conn: return [dict(r) for r in conn.execute(sql, params).fetchall()]
    def fetchone(self, sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute(sql, params).fetchone(); return dict(row) if row else None

def decode_memory(row: dict[str, Any]) -> dict[str, Any]:
    row = dict(row); row["tags"] = json.loads(row.get("tags") or "[]"); row["metadata"] = json.loads(row.get("metadata") or "{}"); row["consolidated"] = bool(row.get("consolidated", 0)); return row

db = Database()
