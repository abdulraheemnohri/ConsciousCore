from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..runtime.policy import classify
from ..runtime.types import RuntimeMode, RuntimeRequest

class SettingsUpdate(BaseModel):
    changes: dict

class RuntimeGenerate(BaseModel):
    prompt: str
    mode: str = "auto"
    privacy: str = "private"
    task_type: str = "general"
    allow_cloud: bool = False
    allow_remote: bool = False
    context: list[str] = []
    parallel_strategy: str = "judge"

class ProviderConfig(BaseModel):
    enabled: bool = False
    models: list[str] = []

def create_router(engine):
    router=APIRouter(prefix="/api/settings/v2",tags=["Settings V2"])
    @router.get("")
    async def get_settings(): return engine.settings_v2.snapshot()
    @router.patch("")
    async def update_settings(body:SettingsUpdate):
        result=engine.settings_v2.update(body.changes); engine.safety.autonomy_level=result["autonomy_level"]; return result
    @router.post("/reset")
    async def reset_settings():
        result=engine.settings_v2.reset(); engine.safety.autonomy_level=result["autonomy_level"]; return result
    @router.get("/runtime")
    async def runtime_snapshot(): return engine.runtime.snapshot()
    @router.get("/runtime/policy")
    async def runtime_policy(text:str,privacy:str="private"):
        d=classify(text,privacy)
        return {"classification":d.classification,"cloud_allowed":d.cloud_allowed,"remote_allowed":d.remote_allowed,"redacted_prompt":d.redacted_prompt,"reasons":d.reasons}
    @router.get("/runtime/providers")
    async def runtime_providers(): return {"providers":engine.runtime.executor.router.providers}
    @router.patch("/runtime/providers/{provider}")
    async def runtime_provider(provider:str,body:ProviderConfig):
        if provider not in {"local","cloud","remote"}: raise HTTPException(400,"unsupported_provider")
        engine.runtime.executor.configure(provider,body.enabled,body.models); return engine.runtime.snapshot()
    @router.post("/runtime/generate")
    async def runtime_generate(body:RuntimeGenerate):
        try: mode=RuntimeMode(body.mode.lower())
        except ValueError: raise HTTPException(400,"invalid_runtime_mode")
        req=RuntimeRequest(prompt=body.prompt,mode=mode,privacy=body.privacy,task_type=body.task_type,allow_cloud=body.allow_cloud,allow_remote=body.allow_remote,require_local_memory=True,metadata={"parallel_strategy":body.parallel_strategy})
        result=await engine.runtime.generate(req,body.context)
        return {"text":result.text,"mode":result.mode,"provider":result.provider,"model":result.model,"confidence":result.confidence,"degraded":result.degraded,"latency_ms":result.latency_ms,"candidates":result.candidates,"policy":result.policy}
    return router
