from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Callable

from .policy import classify
from .types import RuntimeMode, RuntimeRequest


@dataclass(slots=True)
class Route:
    provider: str
    model: str | None
    reason: str


class RuntimeRouter:
    """Policy-first runtime selector. Remote execution is opt-in."""

    def __init__(self) -> None:
        self.providers: dict[str, dict[str, Any]] = {
            "local": {"enabled": True, "models": []},
            "cloud": {"enabled": False, "models": []},
            "remote": {"enabled": False, "models": []},
        }
        self._handlers: dict[str, Callable[..., Any]] = {}

    def register_provider(self, name: str, *, enabled: bool = True, models: list[str] | None = None, handler: Callable[..., Any] | None = None) -> None:
        self.providers[name] = {"enabled": enabled, "models": models or []}
        if handler:
            self._handlers[name] = handler

    def choose(self, request: RuntimeRequest) -> list[Route]:
        boundary = classify(request.prompt, request.privacy)
        mode = request.mode
        if mode == RuntimeMode.AUTO:
            if boundary.classification in {"sensitive", "secret"}:
                mode = RuntimeMode.HYBRID if request.allow_remote and boundary.remote_allowed else RuntimeMode.LOCAL
            elif request.allow_cloud and boundary.cloud_allowed and self.providers.get("cloud", {}).get("enabled"):
                mode = RuntimeMode.CLOUD
            elif request.allow_remote and boundary.remote_allowed and self.providers.get("remote", {}).get("enabled"):
                mode = RuntimeMode.REMOTE
            else:
                mode = RuntimeMode.LOCAL

        if mode == RuntimeMode.CLOUD and not (request.allow_cloud and boundary.cloud_allowed and self.providers.get("cloud", {}).get("enabled")):
            mode = RuntimeMode.LOCAL
        if mode == RuntimeMode.REMOTE and not (request.allow_remote and boundary.remote_allowed and self.providers.get("remote", {}).get("enabled")):
            mode = RuntimeMode.LOCAL

        if mode == RuntimeMode.HYBRID:
            routes = [Route("local", self._first_model("local"), "local cognitive state + remote generation")]
            if request.allow_cloud and boundary.cloud_allowed and self.providers.get("cloud", {}).get("enabled"):
                routes.append(Route("cloud", self._first_model("cloud"), "cloud generation allowed by boundary policy"))
            elif request.allow_remote and boundary.remote_allowed and self.providers.get("remote", {}).get("enabled"):
                routes.append(Route("remote", self._first_model("remote"), "remote generation allowed by boundary policy"))
            return routes

        if mode in {RuntimeMode.PARALLEL, RuntimeMode.DISTRIBUTED}:
            return [Route(p, self._first_model(p), f"{mode.value} candidate") for p in self._available_candidates(request, boundary)]

        provider = mode.value
        return [Route(provider, self._first_model(provider), f"explicit runtime mode: {mode.value}")]

    def explain(self, request: RuntimeRequest) -> dict[str, Any]:
        boundary = classify(request.prompt, request.privacy)
        routes = self.choose(request)
        return {
            "classification": boundary.classification,
            "cloud_allowed": boundary.cloud_allowed and request.allow_cloud,
            "remote_allowed": boundary.remote_allowed and request.allow_remote,
            "routes": [asdict(route) for route in routes],
            "reasons": boundary.reasons,
        }

    def _available_candidates(self, request: RuntimeRequest, boundary: Any) -> list[str]:
        requested = request.candidates or ["local", "remote", "cloud"]
        result = []
        for provider in requested:
            info = self.providers.get(provider, {})
            if not info.get("enabled"):
                continue
            if provider == "cloud" and not (request.allow_cloud and boundary.cloud_allowed):
                continue
            if provider == "remote" and not (request.allow_remote and boundary.remote_allowed):
                continue
            result.append(provider)
        return result or ["local"]

    def _first_model(self, provider: str) -> str | None:
        models = self.providers.get(provider, {}).get("models", [])
        return models[0] if models else None
