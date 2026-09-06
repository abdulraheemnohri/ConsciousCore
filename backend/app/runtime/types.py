from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RuntimeMode(str, Enum):
    LOCAL = "local"
    CLOUD = "cloud"
    REMOTE = "remote"
    HYBRID = "hybrid"
    PARALLEL = "parallel"
    DISTRIBUTED = "distributed"
    AUTO = "auto"


@dataclass(slots=True)
class RuntimeRequest:
    prompt: str
    mode: RuntimeMode = RuntimeMode.AUTO
    privacy: str = "private"
    task_type: str = "general"
    max_latency_ms: int | None = None
    require_local_memory: bool = True
    allow_cloud: bool = False
    allow_remote: bool = False
    candidates: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RuntimeResult:
    text: str
    mode: RuntimeMode
    provider: str
    model: str | None = None
    confidence: float | None = None
    degraded: bool = False
    candidates: list[dict[str, Any]] = field(default_factory=list)
    policy: dict[str, Any] = field(default_factory=dict)
    latency_ms: float | None = None
