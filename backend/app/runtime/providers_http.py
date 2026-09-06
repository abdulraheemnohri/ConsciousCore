from __future__ import annotations
import time
from typing import Any
import httpx

class OpenAICompatibleProvider:
    """Generic OpenAI-compatible chat provider for cloud or self-hosted servers."""
    def __init__(self, name: str, base_url: str, model: str, api_key: str = "", timeout: float = 60.0):
        self.name=name; self.base_url=base_url.rstrip('/'); self.model=model; self.api_key=api_key; self.timeout=timeout
    def _headers(self):
        h={"Content-Type":"application/json"}
        if self.api_key: h["Authorization"]=f"Bearer {self.api_key}"
        return h
    async def health_check(self) -> dict[str, Any]:
        started=time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=min(self.timeout,10)) as client:
                r=await client.get(f"{self.base_url}/v1/models",headers=self._headers()); r.raise_for_status(); data=r.json()
            return {"ok":True,"provider":self.name,"latency_ms":round((time.perf_counter()-started)*1000,2),"models":data.get("data",[]) if isinstance(data,dict) else []}
        except Exception as exc:
            return {"ok":False,"provider":self.name,"latency_ms":round((time.perf_counter()-started)*1000,2),"error":str(exc)}
    async def generate(self,prompt:str,context:list[str]|None=None) -> str:
        memory="\n".join(f"- {x}" for x in (context or []))
        content=f"Relevant memory:\n{memory}\n\nUser:\n{prompt}" if memory else prompt
        payload={"model":self.model,"messages":[{"role":"user","content":content}],"temperature":0.2,"max_tokens":512}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r=await client.post(f"{self.base_url}/v1/chat/completions",headers=self._headers(),json=payload); r.raise_for_status(); data=r.json()
        try: return data["choices"][0]["message"]["content"].strip()
        except (KeyError,IndexError,TypeError) as exc: raise RuntimeError("invalid OpenAI-compatible response") from exc
    async def list_models(self) -> list[dict[str,Any]]:
        async with httpx.AsyncClient(timeout=min(self.timeout,15)) as client:
            r=await client.get(f"{self.base_url}/v1/models",headers=self._headers()); r.raise_for_status(); data=r.json()
        return data.get("data",[]) if isinstance(data,dict) else []
