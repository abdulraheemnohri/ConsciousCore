from __future__ import annotations

import os
import time
from typing import Any

import httpx

from .router import RuntimeRouter
from .types import RuntimeRequest, RuntimeResult


class RuntimeExecutor:
    """Executes routed generations. Local execution stays on the existing model; cloud/remote use OpenAI-compatible HTTP."""

    def __init__(self, local_model: Any, router: RuntimeRouter | None = None) -> None:
        self.local_model = local_model
        self.router = router or RuntimeRouter()
        self.router.register_provider("local", enabled=True, models=[self._model_name()])
        self._configure_from_env()

    def _model_name(self) -> str:
        try:
            return str(self.local_model.info().get("name") or self.local_model.info().get("model") or "local-active")
        except Exception:
            return "local-active"

    def _configure_from_env(self) -> None:
        cloud_enabled = os.getenv("CONSCIOUSCORE_CLOUD_ENABLED", "0").lower() in {"1", "true", "yes", "on"}
        remote_enabled = os.getenv("CONSCIOUSCORE_REMOTE_ENABLED", "0").lower() in {"1", "true", "yes", "on"}
        cloud_model = os.getenv("CONSCIOUSCORE_CLOUD_MODEL", "")
        remote_model = os.getenv("CONSCIOUSCORE_REMOTE_MODEL", "")
        self.router.register_provider("cloud", enabled=cloud_enabled, models=[cloud_model] if cloud_model else [])
        self.router.register_provider("remote", enabled=remote_enabled, models=[remote_model] if remote_model else [])

    def configure(self, provider: str, enabled: bool, models: list[str] | None = None) -> None:
        self.router.register_provider(provider, enabled=enabled, models=models or [])

    async def generate(self, request: RuntimeRequest, context: list[str] | None = None) -> RuntimeResult:
        started = time.perf_counter()
        routes = self.router.choose(request)
        candidates: list[dict[str, Any]] = []
        errors: list[str] = []
        for route in routes:
            try:
                if route.provider == "local":
                    text = await self.local_model.generate(request.prompt, context or [])
                else:
                    text = await self._http_generate(route.provider, request.prompt, context or [], route.model)
                latency = (time.perf_counter() - started) * 1000
                return RuntimeResult(
                    text=text,
                    mode=request.mode.value,
                    provider=route.provider,
                    model=route.model,
                    confidence=1.0 if route.provider == "local" else 0.9,
                    degraded=bool(errors),
                    candidates=candidates,
                    policy=self.router.explain(request),
                    latency_ms=latency,
                )
            except Exception as exc:
                errors.append(f"{route.provider}: {exc}")
                candidates.append({"provider": route.provider, "model": route.model, "error": str(exc)})
        if errors:
            raise RuntimeError("; ".join(errors))
        raise RuntimeError("no runtime route available")

    async def _http_generate(self, provider: str, prompt: str, context: list[str], model: str | None) -> str:
        prefix = "CONSCIOUSCORE_CLOUD" if provider == "cloud" else "CONSCIOUSCORE_REMOTE"
        base_url = os.getenv(f"{prefix}_BASE_URL", "").rstrip("/")
        api_key = os.getenv(f"{prefix}_API_KEY", "")
        if not base_url:
            raise RuntimeError(f"{provider} base URL is not configured")
        model = model or os.getenv(f"{prefix}_MODEL", "")
        if not model:
            raise RuntimeError(f"{provider} model is not configured")
        memories = "\n".join(f"- {x}" for x in context)
        user_prompt = f"Relevant memory:\n{memories}\n\nUser:\n{prompt}" if memories else prompt
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        timeout = float(os.getenv("CONSCIOUSCORE_REMOTE_TIMEOUT", "60"))
        payload = {"model": model, "messages": [{"role": "user", "content": user_prompt}], "temperature": 0.2, "max_tokens": 512}
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(f"{base_url}/v1/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("invalid OpenAI-compatible response") from exc
