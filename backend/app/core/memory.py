from __future__ import annotations
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
import json
import re
from typing import Optional, Any
from ..database import db, decode_memory


# Memory kinds as per ConsciousCore V1 specification
MEMORY_KINDS = {"working", "episodic", "semantic", "procedural", "self", "meta"}

# Additional memory types for specialized storage
SPECIALIZED_MEMORY_TYPES = {
    "working_memories": "working",
    "episodic_memories": "episodic",
    "semantic_memories": "semantic",
    "procedural_memories": "procedural",
    "self_memories": "self",
    "meta_memories": "meta",
    "autobiographical_memories": "autobiographical"
}


@dataclass
class Memory:
    """Represents a memory entry in the system."""
    id: int
    kind: str
    content: str
    importance: float = 0.5
    confidence: float = 0.7
    created_at: str = ""
    metadata: dict | None = None
    tags: list[str] | None = None
    source: str = "system"
    access_count: int = 0
    last_accessed: str | None = None
    consolidated: bool = False
    expires_at: str | None = None  # For working memory
    pinned: bool = False  # For working memory
    
    def json(self) -> dict:
        return asdict(self)


@dataclass
class WorkingMemory:
    """Represents a working memory entry with expiration."""
    id: int
    content: str
    importance: float = 0.5
    confidence: float = 0.7
    tags: list[str] = field(default_factory=list)
    source: str = "system"
    metadata: dict = field(default_factory=dict)
    created_at: str = ""
    expires_at: str | None = None
    pinned: bool = False
    
    def json(self) -> dict:
        return asdict(self)


@dataclass
class EpisodicMemory:
    """Represents an episodic memory entry."""
    id: int
    content: str
    importance: float = 0.5
    confidence: float = 0.7
    tags: list[str] = field(default_factory=list)
    source: str = "system"
    metadata: dict = field(default_factory=dict)
    created_at: str = ""
    event_id: int | None = None
    
    def json(self) -> dict:
        return asdict(self)


@dataclass
class SemanticMemory:
    """Represents a semantic memory entry."""
    id: int
    content: str
    importance: float = 0.5
    confidence: float = 0.7
    tags: list[str] = field(default_factory=list)
    source: str = "system"
    metadata: dict = field(default_factory=dict)
    created_at: str = ""
    
    def json(self) -> dict:
        return asdict(self)


@dataclass
class ProceduralMemory:
    """Represents a procedural memory entry."""
    id: int
    content: str
    importance: float = 0.5
    confidence: float = 0.7
    tags: list[str] = field(default_factory=list)
    source: str = "system"
    metadata: dict = field(default_factory=dict)
    created_at: str = ""
    
    def json(self) -> dict:
        return asdict(self)


@dataclass
class SelfMemory:
    """Represents a self memory entry."""
    id: int
    content: str
    importance: float = 0.5
    confidence: float = 0.7
    tags: list[str] = field(default_factory=list)
    source: str = "system"
    metadata: dict = field(default_factory=dict)
    created_at: str = ""
    
    def json(self) -> dict:
        return asdict(self)


@dataclass
class MetaMemory:
    """Represents a meta memory entry with reliability scoring."""
    id: int
    content: str
    importance: float = 0.5
    confidence: float = 0.7
    tags: list[str] = field(default_factory=list)
    source: str = "system"
    metadata: dict = field(default_factory=dict)
    created_at: str = ""
    reliability: float = 0.7
    
    def json(self) -> dict:
        return asdict(self)


@dataclass
class AutobiographicalMemory:
    """Represents an autobiographical memory entry."""
    id: int
    title: str
    summary: str
    content: str
    importance: float = 0.5
    confidence: float = 0.7
    tags: list[str] = field(default_factory=list)
    source: str = "system"
    metadata: dict = field(default_factory=dict)
    created_at: str = ""
    cycle_id: int | None = None
    goal_id: int | None = None
    plan_id: int | None = None
    
    def json(self) -> dict:
        return asdict(self)


class MemoryStore:
    """Central memory store for ConsciousCore with support for all memory types."""
    
    def __init__(self):
        self._init_specialized_tables()
    
    def _init_specialized_tables(self) -> None:
        """Initialize specialized memory tables if they don't exist."""
        # These tables are already created in database.py, but we ensure they exist
        pass

    # ==================== General Memory Operations ====================
    
    def add(
        self,
        content: str,
        kind: str = "episodic",
        importance: float = 0.5,
        confidence: float = 0.7,
        metadata: dict | None = None,
        tags: list[str] | None = None,
        source: str = "system"
    ) -> Memory:
        """Add a memory to the general memories table."""
        kind = kind if kind in MEMORY_KINDS else "episodic"
        now = datetime.now(timezone.utc).isoformat()
        cur = db.execute(
            "INSERT INTO memories(kind, content, importance, confidence, tags, source, metadata, created_at) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
            (kind, content, float(importance), float(confidence), json.dumps(tags or []), source, json.dumps(metadata or {}), now)
        )
        return self.get(cur.lastrowid)

    def _row_to_memory(self, row: dict) -> Memory:
        """Convert a database row to a Memory object."""
        return Memory(**decode_memory(row))

    def get(self, memory_id: int) -> Memory | None:
        """Get a memory by ID from the general memories table."""
        row = db.fetchone("SELECT * FROM memories WHERE id=?", (memory_id,))
        return self._row_to_memory(row) if row else None

    def _filters(self, kind: str | None, consolidated: bool | None) -> tuple[str, list]:
        """Generate SQL filters for memory queries."""
        clauses = []
        params = []
        if kind in MEMORY_KINDS:
            clauses.append("kind=?")
            params.append(kind)
        if consolidated is not None:
            clauses.append("consolidated=?")
            params.append(int(consolidated))
        return ((" WHERE " + " AND ".join(clauses)) if clauses else "", params)

    def search(
        self,
        q: str,
        limit: int = 8,
        kind: str | None = None,
        consolidated: bool | None = None
    ) -> list[Memory]:
        """Search memories by keyword with scoring."""
        terms = set(re.findall(r"\w+", q.lower()))
        where, params = self._filters(kind, consolidated)
        rows = db.fetchall(
            f"SELECT * FROM memories{where} ORDER BY created_at DESC LIMIT 5000",
            tuple(params)
        )
        scored = []
        now = datetime.now(timezone.utc)
        
        for row in rows:
            words = set(re.findall(r"\w+", row["content"].lower()))
            overlap = len(terms & words) / (len(terms) or 1)
            tag_words = set(re.findall(r"\w+", " ".join(json.loads(row.get("tags") or "[]")).lower()))
            tag_overlap = len(terms & tag_words) / (len(terms) or 1)
            score = 0.60 * overlap + 0.10 * tag_overlap + 0.20 * row["importance"] + 0.10 * row["confidence"]
            if q and score == 0:
                continue
            scored.append((score, self._row_to_memory(row)))

        if not q:
            scored.sort(key=lambda x: x[1].id, reverse=True)
        else:
            scored.sort(key=lambda x: x[0], reverse=True)

        results = [m for _, m in scored[:max(1, min(limit, 1000))]]
        for m in results:
            db.execute(
                "UPDATE memories SET access_count=access_count+1, last_accessed=? WHERE id=?",
                (now.isoformat(), m.id)
            )
        return results

    def recent(self, limit: int = 20, kind: str | None = None, consolidated: bool | None = None) -> list[Memory]:
        """Get recent memories."""
        return self.search("", limit, kind, consolidated)

    def count(self) -> int:
        """Count all memories."""
        return int(db.fetchone("SELECT COUNT(*) AS n FROM memories")["n"])

    def stats(self) -> dict:
        """Get memory statistics."""
        total = self.count()
        by_kind = {r["kind"]: r["n"] for r in db.fetchall("SELECT kind, COUNT(*) n FROM memories GROUP BY kind")}
        consolidated = int(db.fetchone("SELECT COUNT(*) n FROM memories WHERE consolidated=1")["n"])
        return {
            "total": total,
            "consolidated": consolidated,
            "pending": total - consolidated,
            "by_kind": by_kind
        }

    def update(
        self,
        memory_id: int,
        importance: float | None = None,
        confidence: float | None = None,
        kind: str | None = None,
        tags: list[str] | None = None,
        source: str | None = None,
        consolidated: bool | None = None
    ) -> Memory | None:
        """Update a memory entry."""
        current = self.get(memory_id)
        if not current:
            return None
        
        values = []
        params = []
        for col, val in (
            ("importance", importance),
            ("confidence", confidence),
            ("kind", kind),
            ("tags", json.dumps(tags) if tags is not None else None),
            ("source", source),
            ("consolidated", int(consolidated) if consolidated is not None else None)
        ):
            if val is not None:
                values.append(f"{col}=?")
                params.append(val)
        
        if not values:
            return current
        
        params.append(memory_id)
        db.execute(f"UPDATE memories SET {', '.join(values)} WHERE id=?", tuple(params))
        return self.get(memory_id)

    def delete(self, memory_id: int) -> bool:
        """Delete a memory entry."""
        return db.execute("DELETE FROM memories WHERE id=?", (memory_id,)).rowcount > 0

    def consolidate(self) -> int:
        """Consolidate high-importance or frequently accessed memories."""
        return db.execute("UPDATE memories SET consolidated=1 WHERE importance >= 0.65 OR access_count >= 2").rowcount

    def all(self) -> list[Memory]:
        """Get all memories."""
        return self.recent(1000)

    # ==================== Working Memory Operations ====================
    
    def add_working_memory(
        self,
        content: str,
        importance: float = 0.5,
        confidence: float = 0.7,
        tags: list[str] | None = None,
        source: str = "system",
        metadata: dict | None = None,
        expires_at: str | None = None,
        pinned: bool = False
    ) -> WorkingMemory:
        """Add a working memory entry."""
        now = datetime.now(timezone.utc).isoformat()
        cur = db.execute(
            """INSERT INTO working_memories (content, importance, confidence, tags, source, metadata, created_at, expires_at, pinned)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (content, float(importance), float(confidence), json.dumps(tags or []), source, json.dumps(metadata or {}), now, expires_at, int(pinned))
        )
        return self.get_working_memory(cur.lastrowid)

    def get_working_memory(self, memory_id: int) -> WorkingMemory | None:
        """Get a working memory by ID."""
        row = db.fetchone("SELECT * FROM working_memories WHERE id=?", (memory_id,))
        if not row:
            return None
        return WorkingMemory(
            id=row["id"],
            content=row["content"],
            importance=row["importance"],
            confidence=row["confidence"],
            tags=json.loads(row["tags"] or "[]"),
            source=row["source"],
            metadata=json.loads(row["metadata"] or "{}"),
            created_at=row["created_at"],
            expires_at=row["expires_at"],
            pinned=bool(row["pinned"])
        )

    def update_working_memory(
        self,
        memory_id: int,
        content: str | None = None,
        importance: float | None = None,
        confidence: float | None = None,
        tags: list[str] | None = None,
        source: str | None = None,
        metadata: dict | None = None,
        expires_at: str | None = None,
        pinned: bool | None = None
    ) -> WorkingMemory | None:
        """Update a working memory entry."""
        current = self.get_working_memory(memory_id)
        if not current:
            return None
        
        values = []
        params = []
        for col, val in (
            ("content", content),
            ("importance", importance),
            ("confidence", confidence),
            ("tags", json.dumps(tags) if tags is not None else None),
            ("source", source),
            ("metadata", json.dumps(metadata) if metadata is not None else None),
            ("expires_at", expires_at),
            ("pinned", int(pinned) if pinned is not None else None)
        ):
            if val is not None:
                values.append(f"{col}=?")
                params.append(val)
        
        if not values:
            return current
        
        params.append(memory_id)
        db.execute(f"UPDATE working_memories SET {', '.join(values)} WHERE id=?", tuple(params))
        return self.get_working_memory(memory_id)

    def delete_working_memory(self, memory_id: int) -> bool:
        """Delete a working memory entry."""
        return db.execute("DELETE FROM working_memories WHERE id=?", (memory_id,)).rowcount > 0

    def get_all_working_memories(self) -> list[WorkingMemory]:
        """Get all working memories."""
        rows = db.fetchall("SELECT * FROM working_memories ORDER BY created_at DESC")
        return [
            WorkingMemory(
                id=row["id"],
                content=row["content"],
                importance=row["importance"],
                confidence=row["confidence"],
                tags=json.loads(row["tags"] or "[]"),
                source=row["source"],
                metadata=json.loads(row["metadata"] or "{}"),
                created_at=row["created_at"],
                expires_at=row["expires_at"],
                pinned=bool(row["pinned"])
            )
            for row in rows
        ]

    def clear_expired_working_memories(self) -> int:
        """Clear expired working memories."""
        now = datetime.now(timezone.utc).isoformat()
        return db.execute("DELETE FROM working_memories WHERE expires_at IS NOT NULL AND expires_at < ?", (now,)).rowcount

    # ==================== Episodic Memory Operations ====================
    
    def add_episodic_memory(
        self,
        content: str,
        importance: float = 0.5,
        confidence: float = 0.7,
        tags: list[str] | None = None,
        source: str = "system",
        metadata: dict | None = None,
        event_id: int | None = None
    ) -> EpisodicMemory:
        """Add an episodic memory entry."""
        now = datetime.now(timezone.utc).isoformat()
        cur = db.execute(
            """INSERT INTO episodic_memories (content, importance, confidence, tags, source, metadata, created_at, event_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (content, float(importance), float(confidence), json.dumps(tags or []), source, json.dumps(metadata or {}), now, event_id)
        )
        return self.get_episodic_memory(cur.lastrowid)

    def get_episodic_memory(self, memory_id: int) -> EpisodicMemory | None:
        """Get an episodic memory by ID."""
        row = db.fetchone("SELECT * FROM episodic_memories WHERE id=?", (memory_id,))
        if not row:
            return None
        return EpisodicMemory(
            id=row["id"],
            content=row["content"],
            importance=row["importance"],
            confidence=row["confidence"],
            tags=json.loads(row["tags"] or "[]"),
            source=row["source"],
            metadata=json.loads(row["metadata"] or "{}"),
            created_at=row["created_at"],
            event_id=row["event_id"]
        )

    def get_all_episodic_memories(self) -> list[EpisodicMemory]:
        """Get all episodic memories."""
        rows = db.fetchall("SELECT * FROM episodic_memories ORDER BY created_at DESC")
        return [
            EpisodicMemory(
                id=row["id"],
                content=row["content"],
                importance=row["importance"],
                confidence=row["confidence"],
                tags=json.loads(row["tags"] or "[]"),
                source=row["source"],
                metadata=json.loads(row["metadata"] or "{}"),
                created_at=row["created_at"],
                event_id=row["event_id"]
            )
            for row in rows
        ]

    # ==================== Semantic Memory Operations ====================
    
    def add_semantic_memory(
        self,
        content: str,
        importance: float = 0.5,
        confidence: float = 0.7,
        tags: list[str] | None = None,
        source: str = "system",
        metadata: dict | None = None
    ) -> SemanticMemory:
        """Add a semantic memory entry."""
        now = datetime.now(timezone.utc).isoformat()
        cur = db.execute(
            """INSERT INTO semantic_memories (content, importance, confidence, tags, source, metadata, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (content, float(importance), float(confidence), json.dumps(tags or []), source, json.dumps(metadata or {}), now)
        )
        return self.get_semantic_memory(cur.lastrowid)

    def get_semantic_memory(self, memory_id: int) -> SemanticMemory | None:
        """Get a semantic memory by ID."""
        row = db.fetchone("SELECT * FROM semantic_memories WHERE id=?", (memory_id,))
        if not row:
            return None
        return SemanticMemory(
            id=row["id"],
            content=row["content"],
            importance=row["importance"],
            confidence=row["confidence"],
            tags=json.loads(row["tags"] or "[]"),
            source=row["source"],
            metadata=json.loads(row["metadata"] or "{}"),
            created_at=row["created_at"]
        )

    def get_all_semantic_memories(self) -> list[SemanticMemory]:
        """Get all semantic memories."""
        rows = db.fetchall("SELECT * FROM semantic_memories ORDER BY created_at DESC")
        return [
            SemanticMemory(
                id=row["id"],
                content=row["content"],
                importance=row["importance"],
                confidence=row["confidence"],
                tags=json.loads(row["tags"] or "[]"),
                source=row["source"],
                metadata=json.loads(row["metadata"] or "{}"),
                created_at=row["created_at"]
            )
            for row in rows
        ]

    # ==================== Procedural Memory Operations ====================
    
    def add_procedural_memory(
        self,
        content: str,
        importance: float = 0.5,
        confidence: float = 0.7,
        tags: list[str] | None = None,
        source: str = "system",
        metadata: dict | None = None
    ) -> ProceduralMemory:
        """Add a procedural memory entry."""
        now = datetime.now(timezone.utc).isoformat()
        cur = db.execute(
            """INSERT INTO procedural_memories (content, importance, confidence, tags, source, metadata, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (content, float(importance), float(confidence), json.dumps(tags or []), source, json.dumps(metadata or {}), now)
        )
        return self.get_procedural_memory(cur.lastrowid)

    def get_procedural_memory(self, memory_id: int) -> ProceduralMemory | None:
        """Get a procedural memory by ID."""
        row = db.fetchone("SELECT * FROM procedural_memories WHERE id=?", (memory_id,))
        if not row:
            return None
        return ProceduralMemory(
            id=row["id"],
            content=row["content"],
            importance=row["importance"],
            confidence=row["confidence"],
            tags=json.loads(row["tags"] or "[]"),
            source=row["source"],
            metadata=json.loads(row["metadata"] or "{}"),
            created_at=row["created_at"]
        )

    def get_all_procedural_memories(self) -> list[ProceduralMemory]:
        """Get all procedural memories."""
        rows = db.fetchall("SELECT * FROM procedural_memories ORDER BY created_at DESC")
        return [
            ProceduralMemory(
                id=row["id"],
                content=row["content"],
                importance=row["importance"],
                confidence=row["confidence"],
                tags=json.loads(row["tags"] or "[]"),
                source=row["source"],
                metadata=json.loads(row["metadata"] or "{}"),
                created_at=row["created_at"]
            )
            for row in rows
        ]

    # ==================== Self Memory Operations ====================
    
    def add_self_memory(
        self,
        content: str,
        importance: float = 0.5,
        confidence: float = 0.7,
        tags: list[str] | None = None,
        source: str = "system",
        metadata: dict | None = None
    ) -> SelfMemory:
        """Add a self memory entry."""
        now = datetime.now(timezone.utc).isoformat()
        cur = db.execute(
            """INSERT INTO self_memories (content, importance, confidence, tags, source, metadata, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (content, float(importance), float(confidence), json.dumps(tags or []), source, json.dumps(metadata or {}), now)
        )
        return self.get_self_memory(cur.lastrowid)

    def get_self_memory(self, memory_id: int) -> SelfMemory | None:
        """Get a self memory by ID."""
        row = db.fetchone("SELECT * FROM self_memories WHERE id=?", (memory_id,))
        if not row:
            return None
        return SelfMemory(
            id=row["id"],
            content=row["content"],
            importance=row["importance"],
            confidence=row["confidence"],
            tags=json.loads(row["tags"] or "[]"),
            source=row["source"],
            metadata=json.loads(row["metadata"] or "{}"),
            created_at=row["created_at"]
        )

    def get_all_self_memories(self) -> list[SelfMemory]:
        """Get all self memories."""
        rows = db.fetchall("SELECT * FROM self_memories ORDER BY created_at DESC")
        return [
            SelfMemory(
                id=row["id"],
                content=row["content"],
                importance=row["importance"],
                confidence=row["confidence"],
                tags=json.loads(row["tags"] or "[]"),
                source=row["source"],
                metadata=json.loads(row["metadata"] or "{}"),
                created_at=row["created_at"]
            )
            for row in rows
        ]

    # ==================== Meta Memory Operations ====================
    
    def add_meta_memory(
        self,
        content: str,
        importance: float = 0.5,
        confidence: float = 0.7,
        tags: list[str] | None = None,
        source: str = "system",
        metadata: dict | None = None,
        reliability: float = 0.7
    ) -> MetaMemory:
        """Add a meta memory entry."""
        now = datetime.now(timezone.utc).isoformat()
        cur = db.execute(
            """INSERT INTO meta_memories (content, importance, confidence, tags, source, metadata, created_at, reliability)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (content, float(importance), float(confidence), json.dumps(tags or []), source, json.dumps(metadata or {}), now, float(reliability))
        )
        return self.get_meta_memory(cur.lastrowid)

    def get_meta_memory(self, memory_id: int) -> MetaMemory | None:
        """Get a meta memory by ID."""
        row = db.fetchone("SELECT * FROM meta_memories WHERE id=?", (memory_id,))
        if not row:
            return None
        return MetaMemory(
            id=row["id"],
            content=row["content"],
            importance=row["importance"],
            confidence=row["confidence"],
            tags=json.loads(row["tags"] or "[]"),
            source=row["source"],
            metadata=json.loads(row["metadata"] or "{}"),
            created_at=row["created_at"],
            reliability=row["reliability"]
        )

    def get_all_meta_memories(self) -> list[MetaMemory]:
        """Get all meta memories."""
        rows = db.fetchall("SELECT * FROM meta_memories ORDER BY created_at DESC")
        return [
            MetaMemory(
                id=row["id"],
                content=row["content"],
                importance=row["importance"],
                confidence=row["confidence"],
                tags=json.loads(row["tags"] or "[]"),
                source=row["source"],
                metadata=json.loads(row["metadata"] or "{}"),
                created_at=row["created_at"],
                reliability=row["reliability"]
            )
            for row in rows
        ]

    # ==================== Autobiographical Memory Operations ====================
    
    def add_autobiographical_memory(
        self,
        title: str,
        summary: str,
        content: str,
        importance: float = 0.5,
        confidence: float = 0.7,
        tags: list[str] | None = None,
        source: str = "system",
        metadata: dict | None = None,
        cycle_id: int | None = None,
        goal_id: int | None = None,
        plan_id: int | None = None
    ) -> AutobiographicalMemory:
        """Add an autobiographical memory entry."""
        now = datetime.now(timezone.utc).isoformat()
        cur = db.execute(
            """INSERT INTO autobiographical_memories (title, summary, content, importance, confidence, tags, source, metadata, created_at, cycle_id, goal_id, plan_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (title, summary, content, float(importance), float(confidence), json.dumps(tags or []), source, json.dumps(metadata or {}), now, cycle_id, goal_id, plan_id)
        )
        return self.get_autobiographical_memory(cur.lastrowid)

    def get_autobiographical_memory(self, memory_id: int) -> AutobiographicalMemory | None:
        """Get an autobiographical memory by ID."""
        row = db.fetchone("SELECT * FROM autobiographical_memories WHERE id=?", (memory_id,))
        if not row:
            return None
        return AutobiographicalMemory(
            id=row["id"],
            title=row["title"],
            summary=row["summary"],
            content=row["content"],
            importance=row["importance"],
            confidence=row["confidence"],
            tags=json.loads(row["tags"] or "[]"),
            source=row["source"],
            metadata=json.loads(row["metadata"] or "{}"),
            created_at=row["created_at"],
            cycle_id=row["cycle_id"],
            goal_id=row["goal_id"],
            plan_id=row["plan_id"]
        )

    def get_all_autobiographical_memories(self) -> list[AutobiographicalMemory]:
        """Get all autobiographical memories."""
        rows = db.fetchall("SELECT * FROM autobiographical_memories ORDER BY created_at DESC")
        return [
            AutobiographicalMemory(
                id=row["id"],
                title=row["title"],
                summary=row["summary"],
                content=row["content"],
                importance=row["importance"],
                confidence=row["confidence"],
                tags=json.loads(row["tags"] or "[]"),
                source=row["source"],
                metadata=json.loads(row["metadata"] or "{}"),
                created_at=row["created_at"],
                cycle_id=row["cycle_id"],
                goal_id=row["goal_id"],
                plan_id=row["plan_id"]
            )
            for row in rows
        ]

    def search_autobiographical_memories(
        self,
        query: str,
        limit: int = 20,
        cycle_id: int | None = None,
        goal_id: int | None = None
    ) -> list[AutobiographicalMemory]:
        """Search autobiographical memories by title, summary, or content."""
        terms = set(re.findall(r"\w+", query.lower()))
        rows = db.fetchall("SELECT * FROM autobiographical_memories ORDER BY created_at DESC LIMIT 1000")
        scored = []
        
        for row in rows:
            # Search in title, summary, and content
            text = f"{row['title']} {row['summary']} {row['content']}".lower()
            words = set(re.findall(r"\w+", text))
            overlap = len(terms & words) / (len(terms) or 1)
            score = overlap
            
            # Filter by cycle_id or goal_id if provided
            if cycle_id is not None and row["cycle_id"] != cycle_id:
                continue
            if goal_id is not None and row["goal_id"] != goal_id:
                continue
            
            if query and score == 0:
                continue
            scored.append((score, self._row_to_autobiographical_memory(row)))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [m for _, m in scored[:limit]]

    def _row_to_autobiographical_memory(self, row: dict) -> AutobiographicalMemory:
        """Convert a database row to an AutobiographicalMemory object."""
        return AutobiographicalMemory(
            id=row["id"],
            title=row["title"],
            summary=row["summary"],
            content=row["content"],
            importance=row["importance"],
            confidence=row["confidence"],
            tags=json.loads(row["tags"] or "[]"),
            source=row["source"],
            metadata=json.loads(row["metadata"] or "{}"),
            created_at=row["created_at"],
            cycle_id=row["cycle_id"],
            goal_id=row["goal_id"],
            plan_id=row["plan_id"]
        )

    # ==================== Memory Scoring ====================
    
    def score_memory(
        self,
        memory: Memory | WorkingMemory | EpisodicMemory | SemanticMemory | ProceduralMemory | SelfMemory | MetaMemory | AutobiographicalMemory,
        query: str,
        recency_weight: float = 0.15,
        importance_weight: float = 0.15,
        confidence_weight: float = 0.10,
        goal_relation_weight: float = 0.05
    ) -> float:
        """Score a memory based on relevance to a query and other factors."""
        # Semantic similarity (keyword matching)
        terms = set(re.findall(r"\w+", query.lower()))
        content = ""
        if isinstance(memory, Memory):
            content = memory.content
        elif isinstance(memory, WorkingMemory):
            content = memory.content
        elif isinstance(memory, EpisodicMemory):
            content = memory.content
        elif isinstance(memory, SemanticMemory):
            content = memory.content
        elif isinstance(memory, ProceduralMemory):
            content = memory.content
        elif isinstance(memory, SelfMemory):
            content = memory.content
        elif isinstance(memory, MetaMemory):
            content = memory.content
        elif isinstance(memory, AutobiographicalMemory):
            content = f"{memory.title} {memory.summary} {memory.content}"
        
        words = set(re.findall(r"\w+", content.lower()))
        semantic_similarity = len(terms & words) / (len(terms) or 1)
        
        # Tag matching
        tags = getattr(memory, "tags", [])
        tag_words = set(re.findall(r"\w+", " ".join(tags).lower()))
        tag_similarity = len(terms & tag_words) / (len(terms) or 1)
        
        # Recency (newer memories get higher scores)
        created_at = getattr(memory, "created_at", "")
        if created_at:
            try:
                age = (datetime.now(timezone.utc) - datetime.fromisoformat(created_at)).total_seconds()
                recency = max(0, 1 - (age / (24 * 3600 * 30)))  # Normalize to 30 days
            except:
                recency = 0.5
        else:
            recency = 0.5
        
        # Importance and confidence
        importance = getattr(memory, "importance", 0.5)
        confidence = getattr(memory, "confidence", 0.7)
        
        # Goal relation (placeholder for future implementation)
        goal_relation = 0.5
        
        # Calculate final score
        score = (
            0.35 * semantic_similarity +
            0.20 * tag_similarity +
            recency_weight * recency +
            importance_weight * importance +
            confidence_weight * confidence +
            goal_relation_weight * goal_relation
        )
        
        return score
