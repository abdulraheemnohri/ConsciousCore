from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Any


class RuntimeTelemetry:
    """Local-first runtime metrics. No remote telemetry is sent by this module."""

    def __init__(self) -> None:
        self.enabled = False
        self.remote_enabled = False
        self.events = Counter()
        self.latency_ms: list[float] = []

    def record(self, event: str, latency_ms: float | None = None, provider: str | None = None) -> None:
        if not self.enabled:
            return
        self.events[event] += 1
        if provider:
            self.events[f"provider:{provider}"] += 1
        if latency_ms is not None:
            self.latency_ms.append(float(latency_ms))
            if len(self.latency_ms) > 1000:
                self.latency_ms = self.latency_ms[-1000:]

    def snapshot(self) -> dict[str, Any]:
        values = self.latency_ms
        return {
            "enabled": self.enabled,
            "remote_enabled": self.remote_enabled,
            "events": dict(self.events),
            "samples": len(values),
            "avg_latency_ms": round(sum(values) / len(values), 2) if values else 0.0,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
