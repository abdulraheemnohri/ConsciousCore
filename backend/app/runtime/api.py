from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .executor import RuntimeExecutor
from .types import RuntimeMode, RuntimeRequest


class RuntimeGenerate(BaseModel):
    prompt: str = Field(min_length=1, max_length=20000)
    mode: str = "auto"
    privacy: str = "private"
    task_type: str = "chat"
    allow_cloud: bool = False
    allow_remote: bool = False
    context: list[str] = Field(default_factory=list)


class RuntimeConfig(BaseModel):
    mode: str | None = None
    cloud_enabled: bool | None = None
    remote_enabled: bool | None = None
    cloud_models: list[str] | None = None
    remote_models: list[str] | None = None


def create_router(engine):
    router = APIRouter(tags=["runtime"])
    executor = RuntimeExecutor(engine.model)

    @router.get("/runtime")
    async def runtime_status():
        return {"mode": "auto", "providers": executor.router.providers}

    @router.post("/runtime/explain")
    async def runtime_explain(body: RuntimeGenerate):
        try:
            request = RuntimeRequest(
                prompt=body.prompt,
                mode=RuntimeMode(body.mode.lower()),
                privacy=body.privacy,
                task_type=body.task_type,
                allow_cloud=body.allow_cloud,
                allow_remote=body.allow_remote,
            )
            return executor.router.explain(request)
        except ValueError as exc:
            raise HTTPException(400, f"invalid_runtime_mode: {exc}")

    @router.post("/runtime/generate")
    async def runtime_generate(body: RuntimeGenerate):
        try:
            request = RuntimeRequest(
                prompt=body.prompt,
                mode=RuntimeMode(body.mode.lower()),
                privacy=body.privacy,
                task_type=body.task_type,
                allow_cloud=body.allow_cloud,
                allow_remote=body.allow_remote,
            )
            result = await executor.generate(request, body.context)
            return result.__dict__ if hasattr(result, "__dict__") else {
                "text": result.text, "mode": result.mode, "provider": result.provider,
                "model": result.model, "confidence": result.confidence, "degraded": result.degraded,
                "candidates": result.candidates, "policy": result.policy, "latency_ms": result.latency_ms,
            }
        except ValueError as exc:
            raise HTTPException(400, f"invalid_runtime_mode: {exc}")
        except RuntimeError as exc:
            raise HTTPException(503, str(exc))

    @router.post("/runtime/config")
    async def runtime_config(body: RuntimeConfig):
        if body.mode is not None:
            try: RuntimeMode(body.mode.lower())
            except ValueError as exc: raise HTTPException(400, f"invalid_runtime_mode: {exc}")
        if body.cloud_enabled is not None:
            executor.configure("cloud", body.cloud_enabled, body.cloud_models or executor.router.providers.get("cloud", {}).get("models", []))
        if body.remote_enabled is not None:
            executor.configure("remote", body.remote_enabled, body.remote_models or executor.router.providers.get("remote", {}).get("models", []))
        return {"mode": body.mode or "auto", "providers": executor.router.providers}

    return router
