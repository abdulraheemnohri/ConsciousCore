from __future__ import annotations

import asyncio
from typing import Any

from .executor import RuntimeExecutor
from .types import RuntimeMode, RuntimeRequest, RuntimeResult


class RuntimeOrchestrator:
    """Cognitive runtime bridge: single, hybrid, parallel, and failover execution."""

    def __init__(self, local_model: Any) -> None:
        self.executor = RuntimeExecutor(local_model)

    async def generate(self, request: RuntimeRequest, context: list[str] | None = None) -> RuntimeResult:
        if request.mode != RuntimeMode.PARALLEL:
            return await self.executor.generate(request, context)

        routes = self.executor.router.choose(request)
        if not routes:
            return await self.executor.generate(request, context)

        async def run(route):
            child = RuntimeRequest(
                prompt=request.prompt, mode=RuntimeMode(route.provider), privacy=request.privacy,
                task_type=request.task_type, max_latency_ms=request.max_latency_ms,
                require_local_memory=request.require_local_memory, allow_cloud=request.allow_cloud,
                allow_remote=request.allow_remote, candidates=[route.provider], metadata=request.metadata,
            )
            return await self.executor.generate(child, context)

        results = await asyncio.gather(*(run(r) for r in routes), return_exceptions=True)
        successful = [r for r in results if isinstance(r, RuntimeResult)]
        if not successful:
            errors = [str(r) for r in results]
            raise RuntimeError("parallel runtime failed: " + "; ".join(errors))

        # V1 judge policy: prefer the first successful result. A future judge model can
        # score all candidates without exposing hidden chain-of-thought.
        winner = successful[0]
        winner.mode = RuntimeMode.PARALLEL.value
        winner.candidates = [
            {"provider": r.provider, "model": r.model, "latency_ms": r.latency_ms}
            for r in successful
        ]
        return winner
