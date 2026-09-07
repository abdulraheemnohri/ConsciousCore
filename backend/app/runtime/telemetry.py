from __future__ import annotations
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
import json
from ..database import db


class TelemetryMode(Enum):
    OFF = "off"
    LOCAL = "local"
    ANONYMOUS = "anonymous"
    FULL = "full"


class EventType(Enum):
    REQUEST = "request"
    LATENCY = "latency"
    MODEL_USAGE = "model_usage"
    PROVIDER_USAGE = "provider_usage"
    ERROR = "error"
    MEMORY_OPERATION = "memory_operation"
    TOKEN_USAGE = "token_usage"
    RUNTIME_MODE = "runtime_mode"
    SUCCESS = "success"
    FAILURE = "failure"
    PREDICTION = "prediction"
    PREDICTION_ACCURACY = "prediction_accuracy"


@dataclass(slots=True)
class TelemetryEvent:
    event_type: EventType
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Metric:
    name: str
    value: float | int
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    tags: dict[str, Any] = field(default_factory=dict)


class RuntimeTelemetry:
    """Enhanced local-first runtime metrics with privacy controls.
    
    Supports:
    - Local diagnostics (enabled by default)
    - Remote telemetry (disabled by default)
    - Request counting
    - Latency tracking
    - Model/provider usage
    - Error tracking
    - Memory operations
    - Token usage
    - Runtime mode tracking
    - Prediction accuracy
    
    Privacy:
    - Never transmits secrets, private memory, or authentication tokens.
    - Remote telemetry is OFF by default.
    """

    def __init__(self) -> None:
        self.enabled = True  # Local diagnostics enabled by default
        self.remote_enabled = False  # Remote telemetry disabled by default
        self.mode = TelemetryMode.LOCAL
        self.events: Counter = Counter()
        self.latency_ms: list[float] = []
        self.model_usage: Counter = Counter()
        self.provider_usage: Counter = Counter()
        self.errors: Counter = Counter()
        self.memory_operations: Counter = Counter()
        self.token_usage: Counter = Counter()
        self.runtime_modes: Counter = Counter()
        self.successes: Counter = Counter()
        self.failures: Counter = Counter()
        self.predictions: list[dict[str, Any]] = []
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database tables for telemetry."""
        db.execute("""
            CREATE TABLE IF NOT EXISTS telemetry_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                payload TEXT NOT NULL DEFAULT '{}',
                metadata TEXT NOT NULL DEFAULT '{}',
                timestamp TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS telemetry_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                value REAL NOT NULL,
                tags TEXT NOT NULL DEFAULT '{}',
                timestamp TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        db.execute("""
            CREATE INDEX IF NOT EXISTS idx_telemetry_events_type ON telemetry_events(event_type)
        """)
        db.execute("""
            CREATE INDEX IF NOT EXISTS idx_telemetry_events_timestamp ON telemetry_events(timestamp)
        """)
        db.execute("""
            CREATE INDEX IF NOT EXISTS idx_telemetry_metrics_name ON telemetry_metrics(name)
        """)

    def set_mode(self, mode: TelemetryMode | str) -> None:
        """Set the telemetry mode (OFF, LOCAL, ANONYMOUS, FULL)."""
        if isinstance(mode, str):
            self.mode = TelemetryMode(mode)
        else:
            self.mode = mode
        self.remote_enabled = self.mode in (TelemetryMode.ANONYMOUS, TelemetryMode.FULL)

    def record_event(
        self,
        event_type: EventType | str,
        payload: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None
    ) -> None:
        """Record a telemetry event."""
        if isinstance(event_type, str):
            event_type = EventType(event_type)
        
        # Sanitize payload to avoid storing secrets
        sanitized_payload = self._sanitize_payload(payload or {})
        sanitized_metadata = self._sanitize_payload(metadata or {})
        
        # Store in database
        db.execute(
            """INSERT INTO telemetry_events (event_type, payload, metadata, timestamp)
               VALUES (?, ?, ?, ?)""",
            (event_type.value, json.dumps(sanitized_payload), json.dumps(sanitized_metadata), datetime.now(timezone.utc).isoformat())
        )
        
        # Update in-memory counters
        self.events[event_type.value] += 1
        if event_type == EventType.ERROR:
            self.errors[payload.get("error_type", "unknown")] += 1
        elif event_type == EventType.MEMORY_OPERATION:
            self.memory_operations[payload.get("operation", "unknown")] += 1
        elif event_type == EventType.TOKEN_USAGE:
            self.token_usage[payload.get("model", "unknown")] += payload.get("tokens", 0)
        elif event_type == EventType.RUNTIME_MODE:
            self.runtime_modes[payload.get("mode", "unknown")] += 1
        elif event_type == EventType.SUCCESS:
            self.successes[payload.get("task", "unknown")] += 1
        elif event_type == EventType.FAILURE:
            self.failures[payload.get("task", "unknown")] += 1

    def record_request(
        self,
        request_id: str,
        cycle_id: int | None = None,
        runtime_mode: str | None = None,
        provider: str | None = None,
        model: str | None = None,
        latency_ms: float | None = None,
        success: bool = True,
        error: str | None = None
    ) -> None:
        """Record a runtime request."""
        payload = {
            "request_id": request_id,
            "cycle_id": cycle_id,
            "runtime_mode": runtime_mode,
            "provider": provider,
            "model": model,
            "latency_ms": latency_ms,
            "success": success
        }
        if error:
            payload["error"] = error
        
        self.record_event(EventType.REQUEST, payload)
        
        if latency_ms is not None:
            self.latency_ms.append(latency_ms)
            if len(self.latency_ms) > 1000:
                self.latency_ms = self.latency_ms[-1000:]
        
        if provider:
            self.provider_usage[provider] += 1
        if model:
            self.model_usage[model] += 1
        if runtime_mode:
            self.runtime_modes[runtime_mode] += 1
        if success:
            self.successes["total"] += 1
        else:
            self.failures["total"] += 1

    def record_latency(self, latency_ms: float, provider: str | None = None) -> None:
        """Record latency for a request."""
        self.latency_ms.append(latency_ms)
        if len(self.latency_ms) > 1000:
            self.latency_ms = self.latency_ms[-1000:]
        if provider:
            self.provider_usage[provider] += 1

    def record_model_usage(self, model: str, tokens: int | None = None) -> None:
        """Record model usage."""
        self.model_usage[model] += 1
        if tokens is not None:
            self.token_usage[model] += tokens

    def record_error(self, error_type: str, error_message: str | None = None) -> None:
        """Record an error."""
        self.errors[error_type] += 1
        self.record_event(
            EventType.ERROR,
            {"error_type": error_type, "error_message": error_message}
        )

    def record_memory_operation(
        self,
        operation: str,
        memory_id: int | None = None,
        memory_type: str | None = None
    ) -> None:
        """Record a memory operation (read, write, delete)."""
        self.memory_operations[operation] += 1
        self.record_event(
            EventType.MEMORY_OPERATION,
            {"operation": operation, "memory_id": memory_id, "memory_type": memory_type}
        )

    def record_token_usage(self, model: str, tokens: int, direction: str = "input") -> None:
        """Record token usage (input or output)."""
        self.token_usage[f"{model}:{direction}"] += tokens
        self.record_event(
            EventType.TOKEN_USAGE,
            {"model": model, "tokens": tokens, "direction": direction}
        )

    def record_prediction(
        self,
        prediction: str,
        probability: float,
        confidence: float,
        expected_outcome: str | None = None,
        actual_outcome: str | None = None,
        error: float | None = None
    ) -> None:
        """Record a prediction for accuracy tracking."""
        prediction_record = {
            "prediction": prediction,
            "probability": probability,
            "confidence": confidence,
            "expected_outcome": expected_outcome,
            "actual_outcome": actual_outcome,
            "error": error,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.predictions.append(prediction_record)
        if len(self.predictions) > 1000:
            self.predictions = self.predictions[-1000:]
        
        self.record_event(EventType.PREDICTION, prediction_record)
        
        if actual_outcome is not None and error is not None:
            self.record_event(
                EventType.PREDICTION_ACCURACY,
                {"error": error, "confidence": confidence}
            )

    def _sanitize_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Sanitize payload to remove sensitive data."""
        sanitized = {}
        sensitive_keys = {
            "password", "api_key", "token", "secret", "credential",
            "auth", "cookie", "session", "private_key", "otp"
        }
        for key, value in payload.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_payload(value)
            else:
                sanitized[key] = value
        return sanitized

    def get_accuracy_stats(self) -> dict[str, Any]:
        """Calculate prediction accuracy statistics."""
        if not self.predictions:
            return {"count": 0, "avg_error": 0.0, "avg_confidence": 0.0}
        
        errors = [p["error"] for p in self.predictions if p.get("error") is not None]
        confidences = [p["confidence"] for p in self.predictions if p.get("confidence") is not None]
        
        return {
            "count": len(self.predictions),
            "avg_error": round(sum(errors) / len(errors), 4) if errors else 0.0,
            "avg_confidence": round(sum(confidences) / len(confidences), 4) if confidences else 0.0,
            "predictions": self.predictions[-100:]  # Last 100 predictions
        }

    def snapshot(self) -> dict[str, Any]:
        """Get a snapshot of all telemetry metrics."""
        values = self.latency_ms
        
        # Calculate latency stats
        latency_stats = {
            "avg_latency_ms": round(sum(values) / len(values), 2) if values else 0.0,
            "min_latency_ms": min(values) if values else 0.0,
            "max_latency_ms": max(values) if values else 0.0,
            "total_requests": len(values)
        }
        
        # Get prediction accuracy stats
        accuracy_stats = self.get_accuracy_stats()
        
        return {
            "enabled": self.enabled,
            "remote_enabled": self.remote_enabled,
            "mode": self.mode.value,
            "events": dict(self.events),
            "model_usage": dict(self.model_usage),
            "provider_usage": dict(self.provider_usage),
            "errors": dict(self.errors),
            "memory_operations": dict(self.memory_operations),
            "token_usage": dict(self.token_usage),
            "runtime_modes": dict(self.runtime_modes),
            "successes": dict(self.successes),
            "failures": dict(self.failures),
            "latency": latency_stats,
            "prediction_accuracy": accuracy_stats,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

    def get_events(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get recent telemetry events from the database."""
        rows = db.fetchall(
            """SELECT * FROM telemetry_events ORDER BY timestamp DESC LIMIT ?""",
            (limit,)
        )
        return [
            {
                "id": row["id"],
                "event_type": row["event_type"],
                "payload": json.loads(row["payload"]),
                "metadata": json.loads(row["metadata"]),
                "timestamp": row["timestamp"]
            }
            for row in rows
        ]

    def get_metrics(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get recent telemetry metrics from the database."""
        rows = db.fetchall(
            """SELECT * FROM telemetry_metrics ORDER BY timestamp DESC LIMIT ?""",
            (limit,)
        )
        return [
            {
                "id": row["id"],
                "name": row["name"],
                "value": row["value"],
                "tags": json.loads(row["tags"]),
                "timestamp": row["timestamp"]
            }
            for row in rows
        ]

    def clear(self) -> None:
        """Clear in-memory telemetry data (does not affect database)."""
        self.events.clear()
        self.latency_ms.clear()
        self.model_usage.clear()
        self.provider_usage.clear()
        self.errors.clear()
        self.memory_operations.clear()
        self.token_usage.clear()
        self.runtime_modes.clear()
        self.successes.clear()
        self.failures.clear()
        self.predictions.clear()
