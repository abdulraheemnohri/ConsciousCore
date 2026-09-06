from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from .provider_manager import ProviderManager
from .types import RuntimeMode, RuntimeRequest

class ProviderConfig(BaseModel):
    base_url:str=Field(min_length=1,max_length=2000); model:str=Field(min_length=1,max_length=500); api_key:str=""; timeout:float=Field(default=60,ge=1,le=300)
class RuntimeGenerate(BaseModel):
    prompt:str=Field(min_length=1,max_length=20000); mode:str="auto"; privacy:str="private"; allow_cloud:bool=False; allow_remote:bool=False; context:list[str]=Field(default_factory=list); candidates:list[str]=Field(default_factory=list); parallel_strategy:str="judge"

def create_router(engine):
    router=APIRouter(prefix="/api/runtime",tags=["Runtime"]); manager=ProviderManager()
    @router.get("")
    async def snapshot(): return engine.runtime.snapshot()
    @router.get("/providers")
    async def providers(): return {"runtime":engine.runtime.snapshot(),"configured":manager.snapshot()}
    @router.put("/providers/{name}")
    async def configure(name:str,body:ProviderConfig):
        if name not in {"cloud","remote"}: raise HTTPException(400,"provider_must_be_cloud_or_remote")
        manager.register(name,body.base_url,body.model,body.api_key,body.timeout); engine.runtime.executor.configure(name,True,[body.model]); return {"ok":True,"provider":name,"configured":True}
    @router.get("/providers/{name}/health")
    async def health(name:str): return await manager.health(name)
    @router.get("/providers/{name}/models")
    async def models(name:str): return {"provider":name,"models":await manager.models(name)}
    @router.post("/generate")
    async def generate(body:RuntimeGenerate):
        try: mode=RuntimeMode(body.mode.lower())
        except ValueError: raise HTTPException(400,"invalid_runtime_mode")
        request=RuntimeRequest(prompt=body.prompt,mode=mode,privacy=body.privacy,allow_cloud=body.allow_cloud,allow_remote=body.allow_remote,candidates=body.candidates,metadata={"parallel_strategy":body.parallel_strategy})
        try: result=await engine.runtime.generate(request,body.context)
        except RuntimeError as exc: raise HTTPException(503,str(exc))
        return {"text":result.text,"mode":result.mode,"provider":result.provider,"model":result.model,"confidence":result.confidence,"degraded":result.degraded,"latency_ms":result.latency_ms,"candidates":result.candidates,"policy":result.policy}
    return router
