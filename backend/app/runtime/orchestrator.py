from __future__ import annotations

import asyncio
from typing import Any

from .executor import RuntimeExecutor
from .telemetry import RuntimeTelemetry
from .types import RuntimeMode, RuntimeRequest, RuntimeResult


class RuntimeOrchestrator:
    """Cognitive runtime bridge for single, hybrid, parallel and failover execution."""

    def __init__(self, local_model: Any) -> None:
        self.executor = RuntimeExecutor(local_model)
        self.telemetry = RuntimeTelemetry()
        self.last_result: RuntimeResult | None = None

    async def generate(self, request: RuntimeRequest, context: list[str] | None = None) -> RuntimeResult:
        settings = request.metadata.get("settings", {}) if isinstance(request.metadata, dict) else {}
        self.telemetry.enabled = bool(settings.get("telemetry_enabled", self.telemetry.enabled))
        self.telemetry.remote_enabled = bool(settings.get("remote_telemetry_enabled", False))
        if request.mode == RuntimeMode.PARALLEL:
            result = await self._parallel(request, context)
        elif request.mode == RuntimeMode.HYBRID:
            result = await self._hybrid(request, context)
        else:
            result = await self.executor.generate(request, context)
        self.last_result = result
        self.telemetry.record("generation", result.latency_ms, result.provider)
        return result

    async def _hybrid(self, request: RuntimeRequest, context: list[str] | None) -> RuntimeResult:
        """Keep cognition local while selecting a permitted non-local generator."""
        boundary = self.executor.router.explain(request)
        remote_routes = [r for r in boundary["routes"] if r["provider"] in {"cloud", "remote"}]
        if remote_routes:
            provider = remote_routes[0]["provider"]
            child = RuntimeRequest(prompt=request.prompt, mode=RuntimeMode(provider), privacy=request.privacy, task_type=request.task_type, max_latency_ms=request.max_latency_ms, require_local_memory=True, allow_cloud=request.allow_cloud, allow_remote=request.allow_remote, candidates=[provider], metadata={**request.metadata, "hybrid_local_context": True})
            result = await self.executor.generate(child, context)
            result.mode = RuntimeMode.HYBRID.value
            result.policy = boundary
            return result
        child = RuntimeRequest(prompt=request.prompt, mode=RuntimeMode.LOCAL, privacy=request.privacy, task_type=request.task_type, require_local_memory=True, allow_cloud=False, allow_remote=False, candidates=["local"], metadata=request.metadata)
        result = await self.executor.generate(child, context)
        result.mode = RuntimeMode.HYBRID.value
        result.degraded = True
        result.policy = boundary
        return result

    async def _parallel(self, request: RuntimeRequest, context: list[str] | None) -> RuntimeResult:
        routes = self.executor.router.choose(request)
        if not routes:
            return await self.executor.generate(request, context)
        async def run(route):
            child = RuntimeRequest(prompt=request.prompt, mode=RuntimeMode(route.provider), privacy=request.privacy, task_type=request.task_type, max_latency_ms=request.max_latency_ms, require_local_memory=request.require_local_memory, allow_cloud=request.allow_cloud, allow_remote=request.allow_remote, candidates=[route.provider], metadata=request.metadata)
            return await self.executor.generate(child, context)
        results = await asyncio.gather(*(run(r) for r in routes), return_exceptions=True)
        successful = [r for r in results if isinstance(r, RuntimeResult)]
        if not successful:
            raise RuntimeError("parallel runtime failed: " + "; ".join(str(r) for r in results))
        strategy = str(request.metadata.get("parallel_strategy", "judge"))
        winner = min(successful, key=lambda r: r.latency_ms if r.latency_ms is not None else float("inf")) if strategy == "race" else successful[0]
        winner.mode = RuntimeMode.PARALLEL.value
        winner.candidates = [{"provider": r.provider, "model": r.model, "latency_ms": r.latency_ms} for r in successful]
        winner.policy = self.executor.router.explain(request)
        return winner

    def snapshot(self) -> dict[str, Any]:
        return {"providers": self.executor.router.providers, "telemetry": self.telemetry.snapshot(), "last_result": {"mode": self.last_result.mode, "provider": self.last_result.provider, "model": self.last_result.model, "confidence": self.last_result.confidence, "degraded": self.last_result.degraded, "latency_ms": self.last_result.latency_ms} if self.last_result else None}
