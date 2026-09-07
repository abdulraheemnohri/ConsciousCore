from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
import json
import hashlib
from ..database import db


class ReplicationPolicy(Enum):
    LOCAL_ONLY = "local-only"
    LOCAL_REMOTE = "local+remote"
    LOCAL_CLOUD = "local+cloud"
    FEDERATED = "federated"


class ConflictResolutionStrategy(Enum):
    NEWEST = "newest"
    HIGHEST_CONFIDENCE = "highest_confidence"
    HIGHEST_IMPORTANCE = "highest_importance"
    LOCAL_WINS = "local_wins"
    REMOTE_WINS = "remote_wins"
    MERGE = "merge"
    MANUAL_REVIEW = "manual_review"


class SyncStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    FAILED = "failed"
    COMPLETED = "completed"


@dataclass(slots=True)
class MemoryReplica:
    name: str
    enabled: bool = False
    writable: bool = False
    encrypted: bool = True
    endpoint: str | None = None
    latency: int | None = None
    last_sync: str | None = None


@dataclass(slots=True)
class SyncQueueItem:
    id: int | None = None
    memory_id: int | None = None
    node_id: str | None = None
    action: str | None = None  # "create", "update", "delete"
    status: SyncStatus = SyncStatus.PENDING
    retry_count: int = 0
    last_error: str | None = None
    checksum: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(slots=True)
class MemoryConflict:
    id: int | None = None
    memory_id: int | None = None
    node_id: str | None = None
    conflict_type: str | None = None  # "version", "content", "metadata"
    resolution_status: str = "unresolved"
    resolved_by: str | None = None
    resolved_at: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class MemoryFederation:
    """Enhanced policy-aware registry for local, cloud, and remote memory replicas.
    
    Supports:
    - Synchronization queue management
    - Conflict detection and resolution
    - Replication policies (local-only, local+remote, local+cloud, federated)
    - Encryption metadata for secure sync
    """

    def __init__(self) -> None:
        self.replicas: dict[str, MemoryReplica] = {
            "local": MemoryReplica("local", True, True, True),
            "cloud": MemoryReplica("cloud"),
            "remote": MemoryReplica("remote"),
        }
        self.replication_policy = ReplicationPolicy.LOCAL_ONLY
        self.conflict_resolution_strategy = ConflictResolutionStrategy.NEWEST
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database tables for sync queue and conflicts."""
        db.execute("""
            CREATE TABLE IF NOT EXISTS memory_sync_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id INTEGER NOT NULL,
                node_id TEXT NOT NULL,
                action TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                retry_count INTEGER NOT NULL DEFAULT 0,
                last_error TEXT,
                checksum TEXT,
                metadata TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (memory_id) REFERENCES memories(id)
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS memory_conflicts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id INTEGER NOT NULL,
                node_id TEXT NOT NULL,
                conflict_type TEXT NOT NULL,
                resolution_status TEXT NOT NULL DEFAULT 'unresolved',
                resolved_by TEXT,
                resolved_at TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (memory_id) REFERENCES memories(id)
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS memory_replicas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id INTEGER NOT NULL,
                node_id TEXT NOT NULL,
                version INTEGER NOT NULL,
                checksum TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (memory_id) REFERENCES memories(id)
            )
        """)

    def configure(self, name: str, **changes: Any) -> dict[str, Any]:
        """Configure a memory replica."""
        if name not in self.replicas:
            raise KeyError(name)
        replica = self.replicas[name]
        for key, value in changes.items():
            if hasattr(replica, key) and value is not None:
                setattr(replica, key, value)
        return self.snapshot()

    def set_replication_policy(self, policy: ReplicationPolicy | str) -> None:
        """Set the replication policy."""
        if isinstance(policy, str):
            self.replication_policy = ReplicationPolicy(policy)
        else:
            self.replication_policy = policy

    def set_conflict_resolution_strategy(self, strategy: ConflictResolutionStrategy | str) -> None:
        """Set the conflict resolution strategy."""
        if isinstance(strategy, str):
            self.conflict_resolution_strategy = ConflictResolutionStrategy(strategy)
        else:
            self.conflict_resolution_strategy = strategy

    def destinations(self, classification: str = "private") -> list[str]:
        """Determine replication destinations based on data classification."""
        if classification in {"secret", "sensitive"}:
            return ["local"]
        if self.replication_policy == ReplicationPolicy.LOCAL_ONLY:
            return ["local"]
        result = ["local"]
        for name in ("remote", "cloud"):
            if self.replicas[name].enabled and self.replicas[name].writable:
                result.append(name)
        return result

    def add_to_sync_queue(
        self,
        memory_id: int,
        node_id: str,
        action: str,
        checksum: str | None = None,
        metadata: dict[str, Any] | None = None
    ) -> SyncQueueItem:
        """Add a memory operation to the sync queue."""
        metadata_str = json.dumps(metadata or {})
        cur = db.execute(
            """INSERT INTO memory_sync_queue (memory_id, node_id, action, status, checksum, metadata, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))""",
            (memory_id, node_id, action, SyncStatus.PENDING.value, checksum, metadata_str)
        )
        item = SyncQueueItem(
            id=cur.lastrowid,
            memory_id=memory_id,
            node_id=node_id,
            action=action,
            checksum=checksum,
            metadata=metadata or {}
        )
        return item

    def process_sync_queue(self) -> list[SyncQueueItem]:
        """Process pending items in the sync queue."""
        rows = db.fetchall(
            """SELECT * FROM memory_sync_queue WHERE status = ? ORDER BY created_at ASC""",
            (SyncStatus.PENDING.value,)
        )
        items = []
        for row in rows:
            item = SyncQueueItem(
                id=row["id"],
                memory_id=row["memory_id"],
                node_id=row["node_id"],
                action=row["action"],
                status=SyncStatus(row["status"]),
                retry_count=row["retry_count"],
                last_error=row["last_error"],
                checksum=row["checksum"],
                metadata=json.loads(row["metadata"] or "{}"),
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )
            items.append(item)
            # Mark as processing
            db.execute(
                """UPDATE memory_sync_queue SET status = ?, updated_at = datetime('now') WHERE id = ?""",
                (SyncStatus.PROCESSING.value, item.id)
            )
        return items

    def mark_sync_completed(self, item_id: int) -> None:
        """Mark a sync queue item as completed."""
        db.execute(
            """UPDATE memory_sync_queue SET status = ?, updated_at = datetime('now') WHERE id = ?""",
            (SyncStatus.COMPLETED.value, item_id)
        )

    def mark_sync_failed(self, item_id: int, error: str) -> None:
        """Mark a sync queue item as failed and increment retry count."""
        db.execute(
            """UPDATE memory_sync_queue SET status = ?, retry_count = retry_count + 1, last_error = ?, updated_at = datetime('now') WHERE id = ?""",
            (SyncStatus.FAILED.value, error, item_id)
        )

    def retry_failed_items(self, max_retries: int = 3) -> list[SyncQueueItem]:
        """Retry failed sync items that haven't exceeded max retries."""
        rows = db.fetchall(
            """SELECT * FROM memory_sync_queue WHERE status = ? AND retry_count < ? ORDER BY created_at ASC""",
            (SyncStatus.FAILED.value, max_retries)
        )
        items = []
        for row in rows:
            item = SyncQueueItem(
                id=row["id"],
                memory_id=row["memory_id"],
                node_id=row["node_id"],
                action=row["action"],
                status=SyncStatus(row["status"]),
                retry_count=row["retry_count"],
                last_error=row["last_error"],
                checksum=row["checksum"],
                metadata=json.loads(row["metadata"] or "{}"),
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )
            items.append(item)
            # Reset to pending for retry
            db.execute(
                """UPDATE memory_sync_queue SET status = ?, updated_at = datetime('now') WHERE id = ?""",
                (SyncStatus.PENDING.value, item.id)
            )
        return items

    def detect_conflict(
        self,
        memory_id: int,
        node_id: str,
        conflict_type: str
    ) -> MemoryConflict:
        """Detect and register a memory conflict."""
        cur = db.execute(
            """INSERT INTO memory_conflicts (memory_id, node_id, conflict_type, resolution_status, created_at)
               VALUES (?, ?, ?, ?, datetime('now'))""",
            (memory_id, node_id, conflict_type, "unresolved")
        )
        conflict = MemoryConflict(
            id=cur.lastrowid,
            memory_id=memory_id,
            node_id=node_id,
            conflict_type=conflict_type
        )
        return conflict

    def resolve_conflict(
        self,
        conflict_id: int,
        resolution: str,
        resolved_by: str | None = None
    ) -> MemoryConflict | None:
        """Resolve a memory conflict."""
        conflict_row = db.fetchone(
            """SELECT * FROM memory_conflicts WHERE id = ?""",
            (conflict_id,)
        )
        if not conflict_row:
            return None
        
        db.execute(
            """UPDATE memory_conflicts SET resolution_status = ?, resolved_by = ?, resolved_at = datetime('now') WHERE id = ?""",
            (resolution, resolved_by, conflict_id)
        )
        
        resolved_conflict = MemoryConflict(
            id=conflict_row["id"],
            memory_id=conflict_row["memory_id"],
            node_id=conflict_row["node_id"],
            conflict_type=conflict_row["conflict_type"],
            resolution_status=resolution,
            resolved_by=resolved_by,
            resolved_at=datetime.now(timezone.utc).isoformat()
        )
        return resolved_conflict

    def apply_conflict_resolution_strategy(
        self,
        memory_id: int,
        local_memory: dict[str, Any],
        remote_memory: dict[str, Any]
    ) -> dict[str, Any]:
        """Apply the configured conflict resolution strategy."""
        strategy = self.conflict_resolution_strategy
        
        if strategy == ConflictResolutionStrategy.NEWEST:
            local_time = local_memory.get("updated_at", local_memory.get("created_at", ""))
            remote_time = remote_memory.get("updated_at", remote_memory.get("created_at", ""))
            return local_memory if local_time > remote_time else remote_memory
        
        elif strategy == ConflictResolutionStrategy.HIGHEST_CONFIDENCE:
            local_confidence = local_memory.get("confidence", 0)
            remote_confidence = remote_memory.get("confidence", 0)
            return local_memory if local_confidence > remote_confidence else remote_memory
        
        elif strategy == ConflictResolutionStrategy.HIGHEST_IMPORTANCE:
            local_importance = local_memory.get("importance", 0)
            remote_importance = remote_memory.get("importance", 0)
            return local_memory if local_importance > remote_importance else remote_memory
        
        elif strategy == ConflictResolutionStrategy.LOCAL_WINS:
            return local_memory
        
        elif strategy == ConflictResolutionStrategy.REMOTE_WINS:
            return remote_memory
        
        elif strategy == ConflictResolutionStrategy.MERGE:
            # Simple merge: combine content and take highest confidence/importance
            merged = {
                "content": f"{local_memory.get('content', '')} | {remote_memory.get('content', '')}",
                "confidence": max(local_memory.get("confidence", 0), remote_memory.get("confidence", 0)),
                "importance": max(local_memory.get("importance", 0), remote_memory.get("importance", 0)),
                "tags": list(set(local_memory.get("tags", []) + remote_memory.get("tags", []))),
                "metadata": {**local_memory.get("metadata", {}), **remote_memory.get("metadata", {})}
            }
            return merged
        
        else:  # MANUAL_REVIEW
            return {"status": "manual_review_required", "local": local_memory, "remote": remote_memory}

    def generate_checksum(self, content: str) -> str:
        """Generate a checksum for memory content."""
        return hashlib.sha256(content.encode()).hexdigest()

    def add_replica(
        self,
        memory_id: int,
        node_id: str,
        version: int,
        checksum: str
    ) -> None:
        """Add a memory replica record."""
        db.execute(
            """INSERT INTO memory_replicas (memory_id, node_id, version, checksum, created_at, updated_at)
               VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))""",
            (memory_id, node_id, version, checksum)
        )

    def get_replicas(self, memory_id: int) -> list[dict[str, Any]]:
        """Get all replicas for a memory."""
        rows = db.fetchall(
            """SELECT * FROM memory_replicas WHERE memory_id = ?""",
            (memory_id,)
        )
        return [dict(row) for row in rows]

    def snapshot(self) -> dict[str, Any]:
        """Get a snapshot of the current federation state."""
        pending_items = db.fetchall(
            """SELECT COUNT(*) as count FROM memory_sync_queue WHERE status = ?""",
            (SyncStatus.PENDING.value,)
        )[0]["count"]
        
        failed_items = db.fetchall(
            """SELECT COUNT(*) as count FROM memory_sync_queue WHERE status = ?""",
            (SyncStatus.FAILED.value,)
        )[0]["count"]
        
        unresolved_conflicts = db.fetchall(
            """SELECT COUNT(*) as count FROM memory_conflicts WHERE resolution_status = ?""",
            ("unresolved",)
        )[0]["count"]
        
        return {
            "replication_policy": self.replication_policy.value,
            "conflict_resolution_strategy": self.conflict_resolution_strategy.value,
            "replicas": {
                name: {
                    "name": r.name,
                    "enabled": r.enabled,
                    "writable": r.writable,
                    "encrypted": r.encrypted,
                    "endpoint": r.endpoint,
                    "latency": r.latency,
                    "last_sync": r.last_sync
                }
                for name, r in self.replicas.items()
            },
            "sync_queue": {
                "pending": pending_items,
                "failed": failed_items
            },
            "conflicts": {
                "unresolved": unresolved_conflicts
            }
        }
