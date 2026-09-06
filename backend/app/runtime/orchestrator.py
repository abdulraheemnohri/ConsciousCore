from __future__ import annotations

import asyncio
import difflib
from typing import Any

from .executor import RuntimeExecutor
from .telemetry import RuntimeTelemetry
from .types import RuntimeMode, RuntimeRequest, RuntimeResult


class RuntimeOrchestrator:
    """Bounded runtime orchestration with hybrid, parallel and consensus strategies."""
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
        boundary = self.executor.router.explain(request)
        non_local = [r for r in boundary["routes"] if r["provider"] in {"cloud", "remote"}]
        if non_local:
            provider = non_local[0]["provider"]
            child = RuntimeRequest(prompt=request.prompt, mode=RuntimeMode(provider), privacy=request.privacy, task_type=request.task_type, max_latency_ms=request.max_latency_ms, require_local_memory=True, allow_cloud=request.allow_cloud, allow_remote=request.allow_remote, candidates=[provider], metadata={**request.metadata, "hybrid_local_context": True})
            result = await self.executor.generate(child, context)
            result.mode = RuntimeMode.HYBRID.value
            result.policy = boundary
            return result
        child = RuntimeRequest(prompt=request.prompt, mode=RuntimeMode.LOCAL, privacy=request.privacy, task_type=request.task_type, require_local_memory=True, candidates=["local"], metadata=request.metadata)
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
            child = RuntimeRequest(prompt=request.prompt, mode=RuntimeMode(route.provider), privacy=request.privacy, task_type=request.task_type, require_local_memory=request.require_local_memory, allow_cloud=request.allow_cloud, allow_remote=request.allow_remote, candidates=[route.provider], metadata=request.metadata)
            try:
                return await self.executor.generate(child, context)
            except Exception as exc:
                return {"provider": route.provider, "model": route.model, "error": str(exc)}
        results = await asyncio.gather(*(run(r) for r in routes))
        successful = [r for r in results if isinstance(r, RuntimeResult)]
        if not successful:
            raise RuntimeError("parallel runtime failed: " + "; ".join(str(r) for r in results))
        strategy = str(request.metadata.get("parallel_strategy", "judge")).lower()
        if strategy == "race":
            winner = min(successful, key=lambda r: r.latency_ms if r.latency_ms is not None else float("inf"))
        elif strategy == "consensus":
            winner = self._consensus(successful)
        elif strategy == "specialist":
            preferred = str(request.task_type).lower()
            winner = next((r for r in successful if preferred in str(r.model or '').lower()), successful[0])
        else:
            winner = max(successful, key=lambda r: (r.confidence or 0.0) - ((r.latency_ms or 0.0) / 100000.0))
        winner.mode = RuntimeMode.PARALLEL.value
        winner.candidates = [{"provider": r.provider, "model": r.model, "latency_ms": r.latency_ms, "confidence": r.confidence} for r in successful] + [x for x in results if isinstance(x, dict)]
        winner.policy = self.executor.router.explain(request)
        return winner

    @staticmethod
    def _consensus(results: list[RuntimeResult]) -> RuntimeResult:
        best = results[0]; best_score = -1.0
        for candidate in results:
            agreement = sum(difflib.SequenceMatcher(None, candidate.text, other.text).ratio() for other in results) / len(results)
            score = agreement * 0.8 + (candidate.confidence or 0.0) * 0.2
            if score > best_score:
                best, best_score = candidate, score
        return best

    def snapshot(self) -> dict[str, Any]:
        return {"providers": self.executor.router.providers, "telemetry": self.telemetry.snapshot(), "last_result": {"mode": self.last_result.mode, "provider": self.last_result.provider, "model": self.last_result.model, "confidence": self.last_result.confidence, "degraded": self.last_result.degraded, "latency_ms": self.last_result.latency_ms} if self.last_result else None}
