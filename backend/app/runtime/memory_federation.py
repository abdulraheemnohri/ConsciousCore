from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class MemoryReplica:
    name: str
    enabled: bool = False
    writable: bool = False
    encrypted: bool = True
    endpoint: str | None = None


class MemoryFederation:
    """Policy-aware registry for local, cloud and remote memory replicas.

    V1 intentionally does not copy memory automatically. It exposes explicit
    replication decisions so the future sync worker can remain policy-first.
    """

    def __init__(self) -> None:
        self.replicas: dict[str, MemoryReplica] = {
            "local": MemoryReplica("local", True, True, True),
            "cloud": MemoryReplica("cloud"),
            "remote": MemoryReplica("remote"),
        }
        self.replication_policy = "local-only"

    def configure(self, name: str, **changes: Any) -> dict[str, Any]:
        if name not in self.replicas:
            raise KeyError(name)
        replica = self.replicas[name]
        for key, value in changes.items():
            if hasattr(replica, key) and value is not None:
                setattr(replica, key, value)
        return self.snapshot()

    def destinations(self, classification: str = "private") -> list[str]:
        if classification in {"secret", "sensitive"}:
            return ["local"]
        if self.replication_policy == "local-only":
            return ["local"]
        result = ["local"]
        for name in ("remote", "cloud"):
            if self.replicas[name].enabled and self.replicas[name].writable:
                result.append(name)
        return result

    def snapshot(self) -> dict[str, Any]:
        return {
            "replication_policy": self.replication_policy,
            "replicas": {name: {"name": r.name, "enabled": r.enabled, "writable": r.writable, "encrypted": r.encrypted, "endpoint": r.endpoint} for name, r in self.replicas.items()},
        }
