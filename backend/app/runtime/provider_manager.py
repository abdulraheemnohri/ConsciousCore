from __future__ import annotations
import os
from typing import Any
from .providers_http import OpenAICompatibleProvider

class ProviderManager:
    """Runtime provider registry with environment-safe configuration and health discovery."""
    def __init__(self): self.providers: dict[str,OpenAICompatibleProvider]={}; self.configure_from_env()
    def configure_from_env(self):
        self._add_env("cloud","CONSCIOUSCORE_CLOUD")
        self._add_env("remote","CONSCIOUSCORE_REMOTE")
    def _add_env(self,name,prefix):
        base=os.getenv(prefix+"_BASE_URL",""); model=os.getenv(prefix+"_MODEL","")
        if base and model:
            self.providers[name]=OpenAICompatibleProvider(name,base,model,os.getenv(prefix+"_API_KEY",""),float(os.getenv(prefix+"_TIMEOUT","60")))
    def register(self,name:str,base_url:str,model:str,api_key:str="",timeout:float=60):
        self.providers[name]=OpenAICompatibleProvider(name,base_url,model,api_key,timeout); return self.snapshot()
    def get(self,name): return self.providers.get(name)
    async def health(self,name:str):
        provider=self.get(name)
        return {"ok":False,"provider":name,"error":"provider_not_configured"} if not provider else await provider.health_check()
    async def models(self,name:str):
        provider=self.get(name)
        if not provider: return []
        return await provider.list_models()
    def snapshot(self): return {name:{"name":p.name,"base_url":p.base_url,"model":p.model,"configured":True} for name,p in self.providers.items()}
